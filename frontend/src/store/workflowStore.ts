import { create } from 'zustand'
import { persist, createJSONStorage } from 'zustand/middleware'
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
  clearAll: () => void
}

export const useWorkflowStore = create<WorkflowState>()(
  persist(
    (set) => ({
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
        set((state) => {
          const newNodes = [...state.nodes, node]
          return { nodes: newNodes }
        }),
      updateNode: (nodeId, updates) =>
        set((state) => {
          const newNodes = state.nodes.map((node) =>
            node.id === nodeId ? { ...node, ...updates } : node
          )
          return { nodes: newNodes }
        }),
      updateNodeData: (nodeId, dataUpdates) =>
        set((state) => {
          const newNodes = state.nodes.map((node) =>
            node.id === nodeId
              ? { ...node, data: { ...node.data, ...dataUpdates } }
              : node
          )
          return { nodes: newNodes }
        }),
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
        set((state) => {
          const newNodes = state.nodes.map((node) =>
            node.id === nodeId
              ? { ...node, data: { ...node.data, outputPreview: preview } }
              : node
          )
          return { nodes: newNodes }
        }),
      clearAll: () =>
        set({
          nodes: [],
          edges: [],
          workflowId: null,
          runStatus: {
            runId: null,
            status: 'idle',
            nodeStatuses: {},
            nodeOutputs: {},
          },
        }),
    }),
    {
      name: 'workflow-storage',
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({
        nodes: state.nodes,
        edges: state.edges,
        workflowId: state.workflowId,
      }),
    }
  )
)
