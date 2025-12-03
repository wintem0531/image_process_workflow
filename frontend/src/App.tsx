import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { useState } from 'react'
import WorkflowCanvas from './components/WorkflowCanvas'
import NodePalette from './components/NodePalette'
import PropertyPanel from './components/PropertyPanel'
import Toolbar from './components/Toolbar'
import './App.css'

const queryClient = new QueryClient()

function App() {
  const [selectedNode, setSelectedNode] = useState<string | null>(null)

  return (
    <QueryClientProvider client={queryClient}>
      <div className="app">
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
