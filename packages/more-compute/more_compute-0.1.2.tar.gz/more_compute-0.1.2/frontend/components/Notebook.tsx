'use client';

import React, { useState, useEffect, useRef, useCallback, useReducer } from 'react';
import { Cell as CellComponent } from './Cell';
import { Cell, Output, StreamOutput, ExecuteResultOutput, ErrorOutput } from '@/types/notebook';
import { WebSocketService } from '@/lib/websocket-native';
import AddCellButton from './AddCellButton';
import { loadSettings, applyTheme } from '@/lib/settings';

// --- State Management with useReducer ---

interface NotebookState {
  cells: Cell[];
  executingCells: Set<number>;
}

type NotebookAction =
  | { type: 'NOTEBOOK_LOADED'; payload: { cells: Cell[] } }
  | { type: 'EXECUTION_START'; payload: { cell_index: number; execution_count: number } }
  | { type: 'STREAM_OUTPUT'; payload: { cell_index: number; stream: 'stdout' | 'stderr'; text: string } }
  | { type: 'EXECUTE_RESULT'; payload: { cell_index: number; execution_count: number; data: ExecuteResultOutput['data'] } }
  | { type: 'EXECUTION_COMPLETE'; payload: { cell_index: number; result: any } }
  | { type: 'EXECUTION_ERROR'; payload: { cell_index: number; error: Output } }
  | { type: 'NOTEBOOK_UPDATED'; payload: { cells: Cell[] } }
  | { type: 'UPDATE_CELL_SOURCE'; payload: { cell_index: number; source: string } }
  | { type: 'RESET_KERNEL' };

const initialState: NotebookState = {
  cells: [],
  executingCells: new Set(),
};

const initialSettings = loadSettings();
applyTheme(initialSettings.theme);

const coerceToString = (value: unknown): string => {
  if (Array.isArray(value)) {
    return value.join('');
  }
  if (typeof value === 'string') {
    return value;
  }
  return value != null ? String(value) : '';
};

const normalizeError = (error: any): ErrorOutput | undefined => {
  if (!error || typeof error !== 'object') {
    return undefined;
  }

  const tracebackRaw = (error as any).traceback;
  const suggestionsRaw = (error as any).suggestions;

  const traceback = Array.isArray(tracebackRaw)
    ? tracebackRaw.map(coerceToString)
    : coerceToString(tracebackRaw).split('\n');

  const suggestions = Array.isArray(suggestionsRaw)
    ? suggestionsRaw.map(coerceToString)
    : undefined;

  return {
    output_type: 'error',
    ename: coerceToString((error as any).ename ?? 'Error'),
    evalue: coerceToString((error as any).evalue ?? ''),
    traceback,
    error_type: (error as any).error_type,
    suggestions,
  };
};

const normalizeOutputs = (outputs: any): Output[] => {
  if (!Array.isArray(outputs)) {
    return [];
  }

  return outputs.map((output) => {
    if (!output || typeof output !== 'object') {
      return output as Output;
    }

    if (output.output_type === 'stream') {
      const text = coerceToString((output as any).text ?? '');
      return { ...output, text } as StreamOutput;
    }

    if (output.output_type === 'execute_result') {
      const data = { ...(output as any).data };
      if (data && typeof data === 'object') {
        const plain = coerceToString((data as any)['text/plain'] ?? '');
        data['text/plain'] = plain;
      }
      return {
        ...output,
        data,
      } as ExecuteResultOutput;
    }

    if (output.output_type === 'error') {
      return normalizeError(output) as ErrorOutput;
    }

    return output as Output;
  });
};

const normalizeCell = (cell: any, index: number): Cell => {
  const source = coerceToString(cell?.source ?? '');
  const outputs = normalizeOutputs(cell?.outputs);
  const error = normalizeError(cell?.error);
  return {
    id: typeof cell?.id === 'string' && cell.id ? cell.id : `cell-${index}`,
    cell_type: cell?.cell_type || 'code',
    source,
    outputs,
    metadata: cell?.metadata || {},
    execution_count: cell?.execution_count ?? null,
    execution_time: cell?.execution_time,
    error,
  } as Cell;
};

function notebookReducer(state: NotebookState, action: NotebookAction): NotebookState {
  switch (action.type) {
    case 'NOTEBOOK_LOADED':
    case 'NOTEBOOK_UPDATED':
      return {
        ...state,
        cells: action.payload.cells.map((cell, index) => normalizeCell(cell, index)),
      };

    case 'EXECUTION_START': {
      const newExecuting = new Set(state.executingCells);
      newExecuting.add(action.payload.cell_index);
      return {
        ...state,
        executingCells: newExecuting,
        cells: state.cells.map((cell, i) =>
          i === action.payload.cell_index
            ? { ...cell, outputs: [], error: null, execution_count: action.payload.execution_count }
            : cell
        ),
      };
    }

    case 'STREAM_OUTPUT': {
      const { cell_index, stream, text } = action.payload;
      return {
        ...state,
        cells: state.cells.map((cell, i) => {
          if (i !== cell_index) return cell;

          const outputs = [...(cell.outputs || [])];
          const streamIndex = outputs.findIndex(
            (o) => o.output_type === 'stream' && o.name === stream
          );

          if (streamIndex > -1) {
            const streamOutput = outputs[streamIndex] as StreamOutput;
            outputs[streamIndex] = {
              ...streamOutput,
              text: streamOutput.text + text,
            };
          } else {
            outputs.push({ output_type: 'stream', name: stream, text } as StreamOutput);
          }
          return { ...cell, outputs };
        }),
      };
    }

    case 'EXECUTE_RESULT': {
      const { cell_index, execution_count, data } = action.payload;
      return {
        ...state,
        cells: state.cells.map((cell, i) => {
          if (i !== cell_index) return cell;
          const outputs = [...(cell.outputs || [])];
          
          // Check if this is display data (e.g., matplotlib image)
          const hasImageData = (data as any)?.['image/png'] || (data as any)?.['image/jpeg'] || (data as any)?.['image/svg+xml'];
          
          if (hasImageData) {
            // Create display_data output for images (matplotlib plots)
            outputs.push({
              output_type: 'display_data',
              data: data || {},
            } as any);
          } else {
            // Create execute_result output for text results
            outputs.push({
              output_type: 'execute_result',
              execution_count,
              data: {
                ...(data || {}),
                'text/plain': coerceToString(data?.['text/plain'] ?? ''),
              },
            } as ExecuteResultOutput);
          }
          
          return { ...cell, outputs, execution_count };
        }),
      };
    }
    
    case 'EXECUTION_COMPLETE': {
      const payload = action.payload || {};
      const cell_index = payload.cell_index;
      // Support both shapes: { result: {...} } and flat payload {...}
      const result = (payload && payload.result)
        ? payload.result
        : payload || {};
      const newExecuting = new Set(state.executingCells);
      newExecuting.delete(cell_index);
      return {
        ...state,
        executingCells: newExecuting,
        cells: state.cells.map((cell, i) => {
          if (i !== cell_index) return cell;
          const normalizedOutputs = normalizeOutputs(Array.isArray((result as any).outputs) ? (result as any).outputs : []);
          const normalizedError = normalizeError(result?.error);

          const existingOutputs = cell.outputs || [];
          const finalNonStream = normalizedOutputs.filter(o => (o as any).output_type !== 'stream');
          return {
            ...cell,
            ...result,
            outputs: [...existingOutputs, ...finalNonStream],
            execution_count: result?.execution_count ?? cell.execution_count,
            execution_time: result?.execution_time ?? cell.execution_time,
            error: normalizedError,
          };
        }),
      };
    }

    case 'EXECUTION_ERROR': {
        const { cell_index, error } = action.payload;
        const newExecuting = new Set(state.executingCells);
        newExecuting.delete(cell_index);
        const normalizedError = normalizeError(error);
        return {
            ...state,
            executingCells: newExecuting,
            cells: state.cells.map((cell, i) =>
                i === cell_index
                    ? {
                        ...cell,
                        error: normalizedError,
                        outputs: normalizedError
                          ? [...(cell.outputs || []), normalizedError]
                          : cell.outputs || [],
                      }
                    : cell
            ),
        };
    }

    case 'UPDATE_CELL_SOURCE': {
      const { cell_index, source } = action.payload;
      return {
        ...state,
        cells: state.cells.map((cell, i) =>
          i === cell_index ? { ...cell, source } : cell
        ),
      };
    }

    case 'RESET_KERNEL':
        return {
            ...state,
            executingCells: new Set(),
            cells: state.cells.map(cell => ({ ...cell, outputs: [], execution_count: null })),
        };

    default:
      return state;
  }
}

// --- Notebook Component ---

interface NotebookProps {
  notebookName?: string;
}

export const Notebook: React.FC<NotebookProps> = ({ notebookName = 'default' }) => {
  const [state, dispatch] = useReducer(notebookReducer, initialState);
  const { cells, executingCells } = state;
  
  const [currentCellIndex, setCurrentCellIndex] = useState<number | null>(null);
  const [kernelStatus, setKernelStatus] = useState<'connecting' | 'connected' | 'disconnected'>('connecting');
  const wsRef = useRef<WebSocketService | null>(null);

  useEffect(() => {
    const body = document.body;
    const pathAttr = body.getAttribute('data-notebook-path');
    if (pathAttr) {
      document.title = `MoreCompute – ${pathAttr}`;
    }
  }, []);

  // --- Event Handlers ---

  const handleNotebookLoaded = useCallback((data: any) => {
    dispatch({ type: 'NOTEBOOK_LOADED', payload: data });
  }, []);

  const handleExecutionStart = useCallback((data: any) => {
    dispatch({ type: 'EXECUTION_START', payload: data });
  }, []);
  
  const handleStreamOutput = useCallback((data: any) => {
    dispatch({ type: 'STREAM_OUTPUT', payload: data });
  }, []);

  const handleExecutionComplete = useCallback((data: any) => {
    dispatch({ type: 'EXECUTION_COMPLETE', payload: data });
  }, []);

  const handleExecuteResult = useCallback((data: any) => {
    dispatch({
      type: 'EXECUTE_RESULT',
      payload: {
        cell_index: data.cell_index,
        execution_count: data.execution_count,
        data: data.data || {},
      },
    });
  }, []);

  const handleExecutionError = useCallback((data: any) => {
    dispatch({ type: 'EXECUTION_ERROR', payload: data });
  }, []);

  const handleNotebookUpdate = useCallback((data: any) => {
    dispatch({ type: 'NOTEBOOK_UPDATED', payload: data });
  }, []);
  
  const handleKernelStatusUpdate = useCallback((status: 'connecting' | 'connected' | 'disconnected') => {
    setKernelStatus(status);
    const dot = document.getElementById("kernel-status-dot");
    const text = document.getElementById("kernel-status-text");

    if (dot && text) {
      dot.className = 'status-dot'; // Reset classes
      switch (status) {
        case "connecting":
          dot.classList.add("connecting");
          text.textContent = "Connecting...";
          break;
        case "connected":
          dot.classList.add("connected");
          text.textContent = "Kernel Ready";
          break;
        case "disconnected":
          dot.classList.add("disconnected");
          text.textContent = "Kernel Disconnected";
          break;
      }
    }
  }, []);

  useEffect(() => {
    const ws = new WebSocketService();
    wsRef.current = ws;
    handleKernelStatusUpdate('connecting');

    ws.connect('ws://127.0.0.1:8000/ws')
      .then(() => {
        ws.loadNotebook(notebookName || 'default');
      })
      .catch(error => {
        console.error('Failed to connect:', error);
        handleKernelStatusUpdate('disconnected');
      });

    ws.on('connect', () => handleKernelStatusUpdate('connected'));
    ws.on('disconnect', () => handleKernelStatusUpdate('disconnected'));
    ws.on('notebook_loaded', handleNotebookLoaded);
    ws.on('notebook_updated', handleNotebookUpdate);
    ws.on('execution_start', handleExecutionStart);
    ws.on('stream_output', handleStreamOutput);
    ws.on('execution_complete', handleExecutionComplete);
    ws.on('execution_result', handleExecuteResult);
    ws.on('execution_error', handleExecutionError);
    
    return () => ws.disconnect();
  }, [notebookName, handleKernelStatusUpdate, handleNotebookLoaded, handleNotebookUpdate, handleExecutionStart, handleStreamOutput, handleExecuteResult, handleExecutionComplete, handleExecutionError]);

  // Simplified save management - only save on Ctrl+S or Run
  const [saveState, setSaveState] = useState<'idle' | 'saving' | 'saved'>('idle');

  // Simple save function (defined BEFORE cell actions that use it)
  const saveNotebook = useCallback(() => {
    setSaveState('saving');
    wsRef.current?.saveNotebook();

    // Show "Saving..." for 500ms, then "Saved" for 2 seconds
    setTimeout(() => {
      setSaveState('saved');
      setTimeout(() => {
        setSaveState('idle');
      }, 2000);
    }, 500);
  }, []);

  // Keyboard shortcut (Cmd+S / Ctrl+S)
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 's') {
        e.preventDefault();
        saveNotebook();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [saveNotebook]);

  // --- Cell Actions ---

  const executeCell = useCallback((index: number) => {
    const cell = cells[index];
    if (!cell) return;

    if (cell.cell_type === 'markdown') {
      // Save before rendering markdown
      saveNotebook();
      // Markdown rendering is handled locally in Cell.tsx now
      return;
    }

    // Save before executing code
    saveNotebook();
    wsRef.current?.executeCell(index, cell.source);
  }, [cells, saveNotebook]);

  const interruptCell = useCallback((index: number) => {
    wsRef.current?.interruptKernel(index);
  }, []);

  const deleteCell = useCallback((index: number) => {
    wsRef.current?.deleteCell(index);
  }, []);

  const updateCell = useCallback((index: number, source: string) => {
    dispatch({ type: 'UPDATE_CELL_SOURCE', payload: { cell_index: index, source } });
    wsRef.current?.updateCell(index, source);
  }, []);

  const addCell = useCallback((type: 'code' | 'markdown' = 'code', index: number) => {
    wsRef.current?.addCell(index, type);
    setCurrentCellIndex(index);
  }, []);

  const resetKernel = () => {
    if (confirm('Are you sure you want to restart the kernel? All variables will be lost.')) {
      wsRef.current?.resetKernel();
      dispatch({ type: 'RESET_KERNEL' });
    }
  };

  // --- Render ---

  return (
    <>
      {/* Save Status Indicator - show saving and saved states */}
      {saveState !== 'idle' && (
        <div
          style={{
            position: 'fixed',
            bottom: '20px',
            right: '20px',
            padding: '8px 14px',
            borderRadius: '8px',
            fontSize: '12px',
            fontWeight: 500,
            backgroundColor: saveState === 'saved' ? '#10b98114' : '#3b82f614',
            color: saveState === 'saved' ? '#10b981' : '#3b82f6',
            border: `1px solid ${saveState === 'saved' ? '#10b981' : '#3b82f6'}`,
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            zIndex: 1000,
            boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)',
            animation: 'fadeIn 0.2s ease',
          }}
        >
          {saveState === 'saving' && '⟳ Saving...'}
          {saveState === 'saved' && '✓ Saved'}
        </div>
      )}

      {cells.map((cell, index) => (
        <CellComponent
          key={cell.id}
          cell={cell}
          index={index}
          isActive={currentCellIndex === index}
          isExecuting={executingCells.has(index)}
          onExecute={executeCell}
          onInterrupt={interruptCell}
          onDelete={deleteCell}
          onUpdate={updateCell}
          onSetActive={setCurrentCellIndex}
          onAddCell={addCell}
        />
      ))}

      {cells.length === 0 && (
        <div id="empty-state" className="empty-state">
            <div className="add-cell-line" data-position="0">
                <AddCellButton onAddCell={(type) => addCell(type, 0)} />
            </div>
        </div>
      )}
    </>
  );
};