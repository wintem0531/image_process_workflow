import { useState, useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import axios from 'axios'
import { useWorkflowStore } from '../store/workflowStore'
import './PropertyPanel.css'

interface PropertyPanelProps {
  nodeId: string | null
  onClose: () => void
}

export default function PropertyPanel({ nodeId, onClose }: PropertyPanelProps) {
  const { nodes, updateNode } = useWorkflowStore()
  const node = nodes.find((n) => n.id === nodeId)

  const { data: nodeInfo } = useQuery({
    queryKey: ['node-info', node?.data?.nodeType],
    queryFn: async () => {
      if (!node?.data?.nodeType) return null
      const response = await axios.get(`/api/nodes/${node.data.nodeType}`)
      return response.data
    },
    enabled: !!node?.data?.nodeType,
  })

  const [params, setParams] = useState<Record<string, any>>({})

  useEffect(() => {
    if (node) {
      setParams((node.data as any).params || {})
    }
  }, [node])

  if (!nodeId || !node) {
    return null
  }

  const handleParamChange = (key: string, value: any) => {
    const newParams = { ...params, [key]: value }
    setParams(newParams)
    updateNode(nodeId, {
      data: {
        ...node.data,
        params: newParams,
      },
    })
  }

  const renderParamInput = (key: string, schema: any) => {
    const value = params[key] ?? schema.default ?? ''

    switch (schema.type) {
      case 'string':
        if (schema.enum) {
          return (
            <select
              value={value}
              onChange={(e) => handleParamChange(key, e.target.value)}
            >
              {schema.enum.map((opt: string) => (
                <option key={opt} value={opt}>
                  {opt}
                </option>
              ))}
            </select>
          )
        }
        return (
          <input
            type="text"
            value={value}
            onChange={(e) => handleParamChange(key, e.target.value)}
          />
        )
      case 'integer':
      case 'number':
        return (
          <input
            type="number"
            value={value}
            onChange={(e) =>
              handleParamChange(
                key,
                schema.type === 'integer'
                  ? parseInt(e.target.value) || 0
                  : parseFloat(e.target.value) || 0
              )
            }
          />
        )
      case 'boolean':
        return (
          <input
            type="checkbox"
            checked={value}
            onChange={(e) => handleParamChange(key, e.target.checked)}
          />
        )
      default:
        return (
          <textarea
            value={value}
            onChange={(e) => handleParamChange(key, e.target.value)}
            rows={5}
          />
        )
    }
  }

  return (
    <div className="property-panel">
      <div className="panel-header">
        <h3>属性面板</h3>
        <button onClick={onClose}>×</button>
      </div>
      <div className="panel-content">
        <div className="node-info">
          <div className="info-item">
            <label>节点名称</label>
            <div>{node.data.label}</div>
          </div>
          <div className="info-item">
            <label>节点类型</label>
            <div>{node.data.nodeType}</div>
          </div>
        </div>
        {nodeInfo?.param_schema?.properties && (
          <div className="params-section">
            <h4>参数</h4>
            {Object.entries(nodeInfo.param_schema.properties).map(
              ([key, schema]: [string, any]) => (
                <div key={key} className="param-item">
                  <label>{schema.description || key}</label>
                  {renderParamInput(key, schema)}
                </div>
              )
            )}
          </div>
        )}
      </div>
    </div>
  )
}

