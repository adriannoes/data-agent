import { useState, useEffect, useRef } from 'react'
import { RefreshCw, Maximize2 } from 'lucide-react'
import { Button } from './ui/Button'
import { useSSE } from '@/hooks/useSSE'

interface PreviewWindowProps {
  sessionId?: string | null
}

const API_BASE_URL = 'http://localhost:8000'

export function PreviewWindow({ sessionId }: PreviewWindowProps) {
  const [htmlContent, setHtmlContent] = useState<string>('')
  const [isLoading, setIsLoading] = useState(true)
  const iframeRef = useRef<HTMLIFrameElement>(null)

  const handleRefresh = () => {
    if (iframeRef.current) {
      iframeRef.current.contentWindow?.location.reload()
    }
    setIsLoading(true)
  }

  // SSE connection for real-time updates
  const sseUrl = sessionId ? `${API_BASE_URL}/api/stream/${sessionId}` : null

  useSSE(
    sseUrl,
    (message) => {
      if (message.event === 'preview' && message.data.html) {
        setHtmlContent(message.data.html)
        setIsLoading(false)
        
        // Update iframe content
        if (iframeRef.current && iframeRef.current.contentDocument) {
          iframeRef.current.contentDocument.open()
          iframeRef.current.contentDocument.write(message.data.html)
          iframeRef.current.contentDocument.close()
        }
      } else if (message.event === 'status') {
        // Could show status updates in the UI
        console.log('Status:', message.data.message)
      } else if (message.event === 'complete') {
        setIsLoading(false)
      } else if (message.event === 'error') {
        console.error('Error from backend:', message.data.message)
        setIsLoading(false)
      }
    },
    (error) => {
      console.error('SSE connection error:', error)
    }
  )

  // Create blob URL for iframe when htmlContent changes
  useEffect(() => {
    if (htmlContent && iframeRef.current) {
      const blob = new Blob([htmlContent], { type: 'text/html' })
      const url = URL.createObjectURL(blob)
      
      if (iframeRef.current.src !== url) {
        iframeRef.current.src = url
      }
      
      return () => {
        URL.revokeObjectURL(url)
      }
    }
  }, [htmlContent])

  return (
    <div className="flex flex-col h-full bg-background">
      {/* Header */}
      <div className="border-b border-border px-6 py-4 flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold text-foreground">Preview em Tempo Real</h2>
          <p className="text-sm text-muted-foreground">Visualize as mudanças conforme acontecem</p>
        </div>
        <div className="flex gap-2">
          <Button
            variant="ghost"
            size="icon"
            onClick={handleRefresh}
            title="Recarregar preview"
          >
            <RefreshCw className="w-4 h-4" />
          </Button>
          <Button
            variant="ghost"
            size="icon"
            title="Maximizar"
          >
            <Maximize2 className="w-4 h-4" />
          </Button>
        </div>
      </div>

      {/* Iframe Container */}
      <div className="flex-1 relative bg-muted overflow-hidden">
        {isLoading && (
          <div className="absolute inset-0 flex items-center justify-center bg-background/80 z-10">
            <div className="flex flex-col items-center gap-2">
              <RefreshCw className="w-6 h-6 text-primary animate-spin" />
              <p className="text-sm text-muted-foreground">Carregando preview...</p>
            </div>
          </div>
        )}
        <iframe
          ref={iframeRef}
          className="w-full h-full border-0"
          title="Preview"
          onLoad={() => setIsLoading(false)}
          sandbox="allow-same-origin allow-scripts allow-forms allow-popups allow-modals"
        />
      </div>
    </div>
  )
}

