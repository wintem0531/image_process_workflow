import { create } from 'zustand'
import { Node, Edge } from 'reactflow'

interface RunStatus {
  runId: string | null
  status: 'idle' | 'running' | 'completed' | 'failed'
  error?: string
  nodeStatuses: Record<string, string>
  nodeOutputs: Record<string, any[]>
}

interface WorkflowState {
  nodes: Node[]
  edges: Edge[]
  workflowId: string | null
  runStatus: RunStatus
  addNode: (node: Node) => void
  updateNode: (nodeId: string, updates: Partial<Node>) => void
  updateNodeData: (nodeId: string, dataUpdates: Record<string, any>) => void
  deleteNode: (nodeId: string) => void
  updateNodes: (nodes: Node[]) => void
  updateEdges: (edges: Edge[]) => void
  deleteEdge: (edgeId: string) => void
  setWorkflowId: (id: string | null) => void
  setRunStatus: (status: Partial<RunStatus>) => void
  updateNodePreview: (nodeId: string, preview: string) => void
}

export const useWorkflowStore = create<WorkflowState>((set) => ({
  nodes: [],
  edges: [],
  workflowId: null,
  runStatus: {
    runId: null,
    status: 'idle',
    nodeStatuses: {},
    nodeOutputs: {},
  },
  addNode: (node) =>
    set((state) => ({
      nodes: [...state.nodes, node],
    })),
  updateNode: (nodeId, updates) =>
    set((state) => ({
      nodes: state.nodes.map((node) =>
        node.id === nodeId ? { ...node, ...updates } : node
      ),
    })),
  updateNodeData: (nodeId, dataUpdates) =>
    set((state) => ({
      nodes: state.nodes.map((node) =>
        node.id === nodeId
          ? { ...node, data: { ...node.data, ...dataUpdates } }
          : node
      ),
    })),
  deleteNode: (nodeId) =>
    set((state) => ({
      nodes: state.nodes.filter((node) => node.id !== nodeId),
      edges: state.edges.filter(
        (edge) => edge.source !== nodeId && edge.target !== nodeId
      ),
    })),
  updateNodes: (nodes) => set({ nodes }),
  updateEdges: (edges) => set({ edges }),
  deleteEdge: (edgeId) =>
    set((state) => ({
      edges: state.edges.filter((edge) => edge.id !== edgeId),
    })),
  setWorkflowId: (id) => set({ workflowId: id }),
  setRunStatus: (status) =>
    set((state) => ({
      runStatus: { ...state.runStatus, ...status },
    })),
  updateNodePreview: (nodeId, preview) =>
    set((state) => ({
      nodes: state.nodes.map((node) =>
        node.id === nodeId
          ? { ...node, data: { ...node.data, outputPreview: preview } }
          : node
      ),
    })),
}))
