import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { useState, useEffect } from 'react'
import WorkflowCanvas from './components/WorkflowCanvas'
import NodePalette from './components/NodePalette'
import PropertyPanel from './components/PropertyPanel'
import Toolbar from './components/Toolbar'
import { useWorkflowStore } from './store/workflowStore'
import './App.css'

const queryClient = new QueryClient()

function App() {
  const [selectedNode, setSelectedNode] = useState<string | null>(null)
  const [showRestoreNotice, setShowRestoreNotice] = useState(false)
  const nodes = useWorkflowStore((state) => state.nodes)

  // 检测是否从缓存恢复
  useEffect(() => {
    const hasStoredData = localStorage.getItem('workflow-storage')
    if (hasStoredData && nodes.length > 0) {
      setShowRestoreNotice(true)
      setTimeout(() => setShowRestoreNotice(false), 3000)
    }
  }, [])

  return (
    <QueryClientProvider client={queryClient}>
      <div className="app">
        {showRestoreNotice && (
          <div style={{
            position: 'fixed',
            top: '20px',
            right: '20px',
            backgroundColor: '#4caf50',
            color: 'white',
            padding: '12px 20px',
            borderRadius: '4px',
            boxShadow: '0 2px 8px rgba(0,0,0,0.3)',
            zIndex: 1000,
            animation: 'slideIn 0.3s ease-out',
          }}>
            ✅ 已从缓存恢复工作流状态
          </div>
        )}
        <header className="app-header">
          <h1>图像处理工作流平台</h1>
          <Toolbar />
        </header>
        <div className="app-content">
          <NodePalette />
          <WorkflowCanvas
            selectedNode={selectedNode}
            onNodeSelect={setSelectedNode}
          />
          {selectedNode && (
            <PropertyPanel
              nodeId={selectedNode}
              onClose={() => setSelectedNode(null)}
            />
          )}
        </div>
      </div>
    </QueryClientProvider>
  )
}

export default App
