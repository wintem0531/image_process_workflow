import { useCallback, useEffect, useRef } from 'react'
import ReactFlow, {
  Node,
  Edge,
  addEdge,
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  Connection,
  NodeTypes,
  ReactFlowProvider,
  useReactFlow,
  NodeChange,
  EdgeChange,
} from 'reactflow'
import 'reactflow/dist/style.css'
import '@reactflow/node-resizer/dist/style.css'
import axios from 'axios'
import CustomNode from './CustomNode'
import { useWorkflowStore } from '../store/workflowStore'

const nodeTypes: NodeTypes = {
  custom: CustomNode,
}

// 端口数据类型定义
const PORT_DATA_TYPES: Record<string, string> = {
  image: 'image',
  img: 'image',
  contours: 'json',
  rects: 'json',
  data: 'json',
  diff: 'image',
  result: 'any',
  images: 'image[]',
}

// 检查端口类型是否兼容
function arePortsCompatible(sourcePort: string, targetPort: string): boolean {
  const sourceType = PORT_DATA_TYPES[sourcePort] || 'any'
  const targetType = PORT_DATA_TYPES[targetPort] || 'any'
  
  if (sourceType === 'any' || targetType === 'any') return true
  if (sourceType === targetType) return true
  if (sourceType === 'image' && targetType === 'image[]') return true
  
  return false
}

interface WorkflowCanvasProps {
  selectedNode: string | null
  onNodeSelect: (nodeId: string | null) => void
}

function WorkflowCanvasInner({
  selectedNode,
  onNodeSelect,
}: WorkflowCanvasProps) {
  const { 
    nodes: storeNodes, 
    edges: storeEdges, 
    updateNodes, 
    updateEdges, 
    addNode,
    deleteNode,
    deleteEdge,
  } = useWorkflowStore()

  const [nodes, setNodes, onNodesChange] = useNodesState(storeNodes)
  const [edges, setEdges, onEdgesChange] = useEdgesState(storeEdges)
  const reactFlowWrapper = useRef<HTMLDivElement>(null)
  const { screenToFlowPosition } = useReactFlow()

  // 处理键盘删除事件
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Backspace' || event.key === 'Delete') {
        const target = event.target as HTMLElement
        if (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA') {
          return
        }

        const selectedNodes = nodes.filter((node) => node.selected)
        const selectedEdges = edges.filter((edge) => edge.selected)

        if (selectedNodes.length > 0 || selectedEdges.length > 0) {
          event.preventDefault()
          
          selectedNodes.forEach((node) => {
            deleteNode(node.id)
          })
          selectedEdges.forEach((edge) => {
            deleteEdge(edge.id)
          })

          if (selectedNodes.length > 0) {
            onNodeSelect(null)
          }
        }
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [nodes, edges, deleteNode, deleteEdge, onNodeSelect])

  // 处理拖放
  const onDrop = useCallback(
    async (event: React.DragEvent) => {
      event.preventDefault()
      const data = event.dataTransfer.getData('application/reactflow')
      if (!data) return

      const { type, name } = JSON.parse(data)
      
      let nodeInfo = null
      try {
        const response = await axios.get(`/api/nodes/${type}`)
        nodeInfo = response.data
      } catch (e) {
        console.error('获取节点信息失败', e)
      }

      const position = screenToFlowPosition({
        x: event.clientX,
        y: event.clientY,
      })

      const newNode: Node = {
        id: `${type}-${Date.now()}`,
        type: 'custom',
        position,
        data: {
          label: name,
          nodeType: type,
          status: 'pending',
          params: {},
          input_ports: nodeInfo?.input_ports || {},
          output_ports: nodeInfo?.output_ports || {},
        },
      }

      addNode(newNode)
    },
    [addNode, screenToFlowPosition]
  )

  const onDragOver = useCallback((event: React.DragEvent) => {
    event.preventDefault()
    event.dataTransfer.dropEffect = 'move'
  }, [])

  // 连接验证
  const isValidConnection = useCallback(
    (connection: Connection) => {
      const sourceNode = nodes.find((n) => n.id === connection.source)
      const targetNode = nodes.find((n) => n.id === connection.target)
      
      if (!sourceNode || !targetNode) return false
      if (connection.source === connection.target) return false
      
      const sourcePort = connection.sourceHandle || 'output'
      const targetPort = connection.targetHandle || 'input'
      
      return arePortsCompatible(sourcePort, targetPort)
    },
    [nodes]
  )

  const onConnect = useCallback(
    (params: Connection) => {
      const existingEdge = edges.find(
        (e) =>
          e.source === params.source &&
          e.target === params.target &&
          e.sourceHandle === params.sourceHandle &&
          e.targetHandle === params.targetHandle
      )
      if (existingEdge) return

      const newEdges = addEdge(
        {
          ...params,
          type: 'smoothstep',
          animated: false,
          style: { stroke: '#555', strokeWidth: 2 },
        },
        edges
      )
      setEdges(newEdges)
      updateEdges(newEdges)
    },
    [edges, setEdges, updateEdges]
  )

  const onNodeClick = useCallback(
    (_: React.MouseEvent, node: Node) => {
      onNodeSelect(node.id)
    },
    [onNodeSelect]
  )

  const onPaneClick = useCallback(() => {
    onNodeSelect(null)
  }, [onNodeSelect])

  // 处理节点变化
  const handleNodesChange = useCallback(
    (changes: NodeChange[]) => {
      onNodesChange(changes)
    },
    [onNodesChange]
  )

  // 节点拖动结束时同步到 store
  const onNodeDragStop = useCallback(
    (_: React.MouseEvent, node: Node) => {
      const updatedNodes = nodes.map((n) =>
        n.id === node.id ? { ...n, position: node.position } : n
      )
      updateNodes(updatedNodes)
    },
    [nodes, updateNodes]
  )

  // 处理边变化
  const handleEdgesChange = useCallback(
    (changes: EdgeChange[]) => {
      onEdgesChange(changes)
    },
    [onEdgesChange]
  )

  // 同步 store 状态到本地
  useEffect(() => {
    setNodes(storeNodes)
  }, [storeNodes, setNodes])

  useEffect(() => {
    setEdges(storeEdges)
  }, [storeEdges, setEdges])

  return (
    <div ref={reactFlowWrapper} style={{ flex: 1, position: 'relative', background: '#1a1a1a' }}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={handleNodesChange}
        onEdgesChange={handleEdgesChange}
        onConnect={onConnect}
        onNodeClick={onNodeClick}
        onNodeDragStop={onNodeDragStop}
        onPaneClick={onPaneClick}
        onDrop={onDrop}
        onDragOver={onDragOver}
        nodeTypes={nodeTypes}
        isValidConnection={isValidConnection}
        fitView
        defaultEdgeOptions={{
          type: 'smoothstep',
          style: { stroke: '#555', strokeWidth: 2 },
        }}
        connectionLineStyle={{ stroke: '#007acc', strokeWidth: 2 }}
        snapToGrid
        snapGrid={[15, 15]}
        nodesDraggable={true}
        nodesConnectable={true}
        elementsSelectable={true}
      >
        <Background color="#333" gap={20} />
        <Controls />
        <MiniMap
          nodeColor={(node) => {
            const status = (node.data as any)?.status
            if (status === 'success') return '#4caf50'
            if (status === 'failed') return '#f44336'
            if (status === 'running') return '#007acc'
            return '#555'
          }}
          maskColor="rgba(0, 0, 0, 0.8)"
        />
      </ReactFlow>
    </div>
  )
}

export default function WorkflowCanvas(props: WorkflowCanvasProps) {
  return (
    <ReactFlowProvider>
      <WorkflowCanvasInner {...props} />
    </ReactFlowProvider>
  )
}
