import { useState, useMemo } from 'react'
import { useQuery } from '@tanstack/react-query'
import axios from 'axios'
import { useWorkflowStore } from '../store/workflowStore'
import './NodePalette.css'

interface NodeInfo {
  type: string
  name: string
  description: string
  input_ports: Record<string, string>
  output_ports: Record<string, string>
}

const nodeCategories: Record<string, string[]> = {
  '输入': ['ImageInput', 'JSONInput'],
  '基本处理': ['Resize', 'Crop', 'Grayscale', 'Threshold', 'Blur', 'GaussianBlur'],
  '形态学': ['Erode', 'Dilate', 'Open', 'Close'],
  '几何': ['FindContours', 'BoundingRect', 'MinAreaRect'],
  '绘制': ['DrawRectangle', 'DrawText', 'Overlay'],
  '拼接': ['ConcatHorizontal', 'ConcatVertical', 'Tile'],
  '数据': ['JSONOutput'],
  '查看器': ['ImageViewer', 'DiffViewer'],
  '脚本': ['PythonSnippet'],
}

export default function NodePalette() {
  const [searchTerm, setSearchTerm] = useState('')
  const { addNode } = useWorkflowStore()

  const { data: nodes = [] } = useQuery<NodeInfo[]>({
    queryKey: ['nodes'],
    queryFn: async () => {
      const response = await axios.get('/api/nodes')
      return response.data
    },
  })

  const handleDragStart = (e: React.DragEvent, nodeType: string, nodeName: string) => {
    e.dataTransfer.setData('application/reactflow', JSON.stringify({ type: nodeType, name: nodeName }))
    e.dataTransfer.effectAllowed = 'move'
  }

  const filteredCategories = useMemo(() => {
    if (!searchTerm) return nodeCategories

    const filtered: Record<string, string[]> = {}
    for (const [category, types] of Object.entries(nodeCategories)) {
      const matching = types.filter((type) => {
        const node = nodes.find((n) => n.type === type)
        return (
          node &&
          (node.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
           node.description.toLowerCase().includes(searchTerm.toLowerCase()))
        )
      })
      if (matching.length > 0) {
        filtered[category] = matching
      }
    }
    return filtered
  }, [searchTerm, nodes])

  return (
    <div className="node-palette">
      <div className="palette-header">
        <h3>节点面板</h3>
        <input
          type="text"
          placeholder="搜索节点..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="search-input"
        />
      </div>
      <div className="palette-content">
        {Object.entries(filteredCategories).map(([category, types]) => (
          <div key={category} className="category">
            <div className="category-title">{category}</div>
            {types.map((type) => {
              const node = nodes.find((n) => n.type === type)
              if (!node) return null
              return (
                <div
                  key={type}
                  className="node-item"
                  draggable
                  onDragStart={(e) => handleDragStart(e, type, node.name)}
                >
                  <div className="node-name">{node.name}</div>
                  <div className="node-desc">{node.description}</div>
                </div>
              )
            })}
          </div>
        ))}
      </div>
    </div>
  )
}


