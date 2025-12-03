import { memo, useEffect, useState } from 'react'
import { Handle, Position, NodeProps } from 'reactflow'
import { NodeResizer } from '@reactflow/node-resizer'
import './CustomNode.css'

interface PortInfo {
  name: string
  description: string
  dataType?: string
}

interface OutputData {
  type: 'image' | 'json' | 'text'
  value: any
  preview?: string
}

interface CustomNodeData {
  label: string
  nodeType: string
  status?: 'pending' | 'running' | 'success' | 'failed'
  preview?: string
  inputPreview?: string
  outputPreview?: string
  outputData?: OutputData[]
  params?: Record<string, any>
  input_ports?: Record<string, string>
  output_ports?: Record<string, string>
}

// 端口数据类型映射
const PORT_TYPE_COLORS: Record<string, string> = {
  image: '#4caf50',
  json: '#ff9800',
  text: '#2196f3',
  any: '#9c27b0',
}

function getPortType(portName: string): string {
  if (portName.includes('image') || portName === 'img' || portName === 'diff') return 'image'
  if (portName.includes('contour') || portName.includes('rect') || portName === 'data') return 'json'
  return 'any'
}

function CustomNode({ id, data, selected }: NodeProps<CustomNodeData>) {
  const [inputPorts, setInputPorts] = useState<PortInfo[]>([])
  const [outputPorts, setOutputPorts] = useState<PortInfo[]>([])

  // 从节点信息获取端口
  useEffect(() => {
    if (data.input_ports) {
      setInputPorts(
        Object.entries(data.input_ports).map(([name, desc]) => ({
          name,
          description: desc as string,
          dataType: getPortType(name),
        }))
      )
    }
    if (data.output_ports) {
      setOutputPorts(
        Object.entries(data.output_ports).map(([name, desc]) => ({
          name,
          description: desc as string,
          dataType: getPortType(name),
        }))
      )
    }
  }, [data.input_ports, data.output_ports])

  const statusColors: Record<string, string> = {
    pending: '#555',
    running: '#007acc',
    success: '#4caf50',
    failed: '#f44336',
  }

  const statusBgColors: Record<string, string> = {
    pending: '#2d2d30',
    running: '#1a3a5c',
    success: '#1a3a1a',
    failed: '#3d1a1a',
  }

  // 渲染输出数据
  const renderOutputData = () => {
    // 如果有图像预览
    if (data.outputPreview && typeof data.outputPreview === 'string' && data.outputPreview.startsWith('data:image')) {
      return (
        <div className="preview-section">
          <div className="preview-label">输出</div>
          <img src={data.outputPreview} alt="output" className="preview-image" />
        </div>
      )
    }

    // 如果有其他类型的输出数据
    if (data.outputData && data.outputData.length > 0) {
      return (
        <div className="output-data-section">
          {data.outputData.map((output, idx) => (
            <div key={idx} className="output-data-item">
              {output.type === 'image' && output.preview && (
                <img src={output.preview} alt="output" className="preview-image" />
              )}
              {output.type === 'json' && (
                <div className="json-output">
                  <div className="preview-label">JSON 数据</div>
                  <div className="json-list">
                    {Array.isArray(output.value) ? (
                      output.value.slice(0, 5).map((item: any, i: number) => (
                        <div key={i} className="json-list-item">
                          {typeof item === 'object' 
                            ? Object.entries(item).slice(0, 3).map(([k, v]) => (
                                <span key={k} className="json-field">
                                  <span className="json-key">{k}:</span>
                                  <span className="json-value">{String(v).slice(0, 10)}</span>
                                </span>
                              ))
                            : String(item).slice(0, 30)
                          }
                        </div>
                      ))
                    ) : typeof output.value === 'object' ? (
                      Object.entries(output.value).slice(0, 5).map(([k, v]) => (
                        <div key={k} className="json-list-item">
                          <span className="json-key">{k}:</span>
                          <span className="json-value">{JSON.stringify(v).slice(0, 30)}</span>
                        </div>
                      ))
                    ) : (
                      <div className="json-list-item">{String(output.value).slice(0, 50)}</div>
                    )}
                    {Array.isArray(output.value) && output.value.length > 5 && (
                      <div className="json-more">... 还有 {output.value.length - 5} 项</div>
                    )}
                  </div>
                </div>
              )}
              {output.type === 'text' && (
                <div className="text-output">
                  {String(output.value).slice(0, 100)}
                </div>
              )}
            </div>
          ))}
        </div>
      )
    }

    return null
  }

  const minWidth = 200
  const minHeight = 100

  return (
    <>
      {/* 节点调整大小控件 */}
      <NodeResizer
        color={statusColors[data.status || 'pending']}
        isVisible={selected}
        minWidth={minWidth}
        minHeight={minHeight}
        handleStyle={{ 
          width: 10, 
          height: 10,
          borderRadius: 2,
        }}
        lineStyle={{
          borderWidth: 1,
        }}
      />
      
      <div
        className={`custom-node ${selected ? 'selected' : ''}`}
        style={{
          borderColor: statusColors[data.status || 'pending'],
          background: statusBgColors[data.status || 'pending'],
          width: '100%',
          height: '100%',
          minWidth: minWidth,
          minHeight: minHeight,
        }}
      >
        {/* 节点标题 - 可拖动区域 */}
        <div 
          className="node-header drag-handle" 
          style={{ borderColor: statusColors[data.status || 'pending'] }}
        >
          <span className="node-type">{data.nodeType}</span>
          <span className="node-label">{data.label}</span>
          {data.status === 'running' && <span className="status-indicator running">●</span>}
          {data.status === 'success' && <span className="status-indicator success">✓</span>}
          {data.status === 'failed' && <span className="status-indicator failed">✗</span>}
        </div>

        {/* 节点内容 */}
        <div className="node-content">
          {/* 左侧输入端口 */}
          <div className="ports-left">
            {inputPorts.map((port) => (
              <div key={port.name} className="port-row input-port">
                <Handle
                  type="target"
                  position={Position.Left}
                  id={port.name}
                  className="port-handle input-handle"
                  style={{ 
                    borderColor: PORT_TYPE_COLORS[port.dataType || 'any'],
                    background: '#1e1e1e',
                  }}
                />
                <span className="port-label" title={port.description}>
                  <span className="port-arrow" style={{ color: PORT_TYPE_COLORS[port.dataType || 'any'] }}>▶</span>
                  <span className="port-name">{port.name}</span>
                  <span className="port-type-badge" style={{ background: PORT_TYPE_COLORS[port.dataType || 'any'] }}>
                    {port.dataType}
                  </span>
                </span>
              </div>
            ))}
            {inputPorts.length === 0 && (
              <div className="no-ports">无输入</div>
            )}
          </div>

          {/* 中间预览区域 */}
          <div className="preview-area">
            {/* 输入预览 */}
            {data.inputPreview && (
              <div className="preview-section">
                <div className="preview-label">输入</div>
                <img src={data.inputPreview} alt="input" className="preview-image" />
              </div>
            )}
            
            {/* 输出预览/数据 */}
            {renderOutputData()}
            
            {/* 单一预览（兼容旧数据） */}
            {data.preview && !data.inputPreview && !data.outputPreview && !data.outputData && (
              <img src={data.preview} alt="preview" className="preview-image" />
            )}

            {/* 无预览时显示参数摘要 */}
            {!data.preview && !data.inputPreview && !data.outputPreview && !data.outputData && 
             data.params && Object.keys(data.params).length > 0 && (
              <div className="params-summary">
                {Object.entries(data.params).slice(0, 4).map(([key, value]) => (
                  <div key={key} className="param-item">
                    <span className="param-key">{key}:</span>
                    <span className="param-value">{String(value).slice(0, 15)}</span>
                  </div>
                ))}
              </div>
            )}

            {/* 完全空状态 */}
            {!data.preview && !data.inputPreview && !data.outputPreview && !data.outputData &&
             (!data.params || Object.keys(data.params).length === 0) && (
              <div className="empty-state">
                <span className="empty-icon">📷</span>
                <span className="empty-text">运行后显示结果</span>
              </div>
            )}
          </div>

          {/* 右侧输出端口 */}
          <div className="ports-right">
            {outputPorts.map((port) => (
              <div key={port.name} className="port-row output-port">
                <span className="port-label" title={port.description}>
                  <span className="port-type-badge" style={{ background: PORT_TYPE_COLORS[port.dataType || 'any'] }}>
                    {port.dataType}
                  </span>
                  <span className="port-name">{port.name}</span>
                  <span className="port-arrow" style={{ color: PORT_TYPE_COLORS[port.dataType || 'any'] }}>▶</span>
                </span>
                <Handle
                  type="source"
                  position={Position.Right}
                  id={port.name}
                  className="port-handle output-handle"
                  style={{ 
                    borderColor: PORT_TYPE_COLORS[port.dataType || 'any'],
                    background: '#1e1e1e',
                  }}
                />
              </div>
            ))}
            {outputPorts.length === 0 && (
              <div className="no-ports">无输出</div>
            )}
          </div>
        </div>
      </div>
    </>
  )
}

export default memo(CustomNode)
