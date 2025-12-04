import { useMutation, useQuery } from '@tanstack/react-query'
import axios from 'axios'
import { useWorkflowStore } from '../store/workflowStore'
import './Toolbar.css'

export default function Toolbar() {
  const { nodes, edges, workflowId, runStatus, setWorkflowId, setRunStatus, updateNodeData, clearAll } = useWorkflowStore()

  // 运行工作流
  const runMutation = useMutation({
    mutationFn: async () => {
      // 转换节点和边为API格式
      const workflowNodes = nodes.map((node) => ({
        id: node.id,
        type: (node.data as any).nodeType,
        params: (node.data as any).params || {},
        inputs: [],
        outputs: Object.keys((node.data as any).output_ports || {}),
        position: { x: node.position.x, y: node.position.y },
      }))

      const workflowLinks = edges.map((edge) => ({
        from: {
          node: edge.source,
          port: edge.sourceHandle || 'output',
        },
        to: {
          node: edge.target,
          port: edge.targetHandle || 'input',
        },
      }))

      // 创建或更新工作流
      let wfId = workflowId
      if (!wfId) {
        const createResponse = await axios.post('/api/workflows', {
          name: '临时工作流',
          nodes: workflowNodes,
          links: workflowLinks,
        })
        wfId = createResponse.data.workflow_id
        setWorkflowId(wfId)
      } else {
        await axios.put(`/api/workflows/${wfId}`, {
          nodes: workflowNodes,
          links: workflowLinks,
        })
      }

      // 重置所有节点状态
      nodes.forEach((node) => {
        updateNodeData(node.id, { 
          status: 'pending', 
          outputPreview: null,
          outputData: null,
        })
      })

      // 执行工作流
      const runResponse = await axios.post('/api/runs', {
        workflow_id: wfId,
        max_concurrent: 4,
      })

      return runResponse.data.run_id
    },
    onSuccess: (runId) => {
      setRunStatus({ runId, status: 'running' })
    },
    onError: (error: any) => {
      setRunStatus({ status: 'failed', error: error.message })
    },
  })

  // 轮询运行状态
  useQuery({
    queryKey: ['run-status', runStatus.runId],
    queryFn: async () => {
      if (!runStatus.runId) return null
      const response = await axios.get(`/api/runs/${runStatus.runId}`)
      const data = response.data

      // 更新节点状态和输出
      Object.entries(data.node_statuses || {}).forEach(([nodeId, status]) => {
        updateNodeData(nodeId, { status })
      })

      // 更新节点输出数据
      Object.entries(data.node_outputs || {}).forEach(([nodeId, outputs]: [string, any]) => {
        if (outputs && outputs.length > 0) {
          // 处理不同类型的输出
          const outputData: any[] = []
          let imagePreview: string | null = null

          outputs.forEach((output: any) => {
            if (output.data_type === 'image') {
              // 图像输出
              if (output.value && typeof output.value === 'string' && output.value.startsWith('data:image')) {
                imagePreview = output.value
                outputData.push({
                  type: 'image',
                  value: null,
                  preview: output.value,
                })
              }
            } else if (output.data_type === 'json') {
              // JSON 输出
              outputData.push({
                type: 'json',
                value: output.value,
              })
            } else {
              // 文本输出
              outputData.push({
                type: 'text',
                value: output.value,
              })
            }
          })

          updateNodeData(nodeId, { 
            outputPreview: imagePreview,
            outputData: outputData.length > 0 ? outputData : null,
          })
        }
      })

      if (data.status === 'completed' || data.status === 'failed') {
        setRunStatus({
          status: data.status,
          error: data.error,
          nodeStatuses: data.node_statuses,
          nodeOutputs: data.node_outputs,
        })
      }

      return data
    },
    enabled: runStatus.status === 'running' && !!runStatus.runId,
    refetchInterval: 500,
  })

  // 导出代码
  const exportMutation = useMutation({
    mutationFn: async (mode: 'script' | 'module') => {
      if (!workflowId) throw new Error('请先运行工作流')
      const response = await axios.post(`/api/export/${workflowId}?mode=${mode}`)
      return response.data
    },
    onSuccess: (data) => {
      const blob = new Blob([data.code], { type: 'text/python' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `${data.workflow_name || 'workflow'}.py`
      a.click()
      URL.revokeObjectURL(url)
    },
  })

  const isRunning = runStatus.status === 'running' || runMutation.isPending

  const handleClearAll = () => {
    if (confirm('确定要清空所有节点吗？此操作将清除缓存并重置工作流。')) {
      clearAll()
      setWorkflowId(null)
    }
  }

  return (
    <div className="toolbar">
      <button
        className={`toolbar-btn primary ${isRunning ? 'running' : ''}`}
        onClick={() => runMutation.mutate()}
        disabled={isRunning || nodes.length === 0}
      >
        {isRunning ? (
          <>
            <span className="spinner"></span>
            运行中...
          </>
        ) : (
          <>
            <span className="icon">▶</span>
            运行
          </>
        )}
      </button>

      <div className="toolbar-divider"></div>

      <button
        className="toolbar-btn"
        onClick={() => exportMutation.mutate('script')}
        disabled={!workflowId || exportMutation.isPending}
      >
        <span className="icon">📄</span>
        导出脚本
      </button>

      <button
        className="toolbar-btn"
        onClick={() => exportMutation.mutate('module')}
        disabled={!workflowId || exportMutation.isPending}
      >
        <span className="icon">📦</span>
        导出模块
      </button>

      <div className="toolbar-divider"></div>

      <button
        className="toolbar-btn"
        onClick={handleClearAll}
        disabled={isRunning}
        title="清空所有节点并重置工作流"
      >
        <span className="icon">🗑️</span>
        清空
      </button>

      {runStatus.status === 'failed' && runStatus.error && (
        <div className="toolbar-error" title={runStatus.error}>
          ⚠️ 运行失败
        </div>
      )}

      {runStatus.status === 'completed' && (
        <div className="toolbar-success">
          ✓ 运行完成
        </div>
      )}
    </div>
  )
}
