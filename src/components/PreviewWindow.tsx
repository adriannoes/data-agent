import { useState, useEffect } from 'react'
import { RefreshCw, Maximize2 } from 'lucide-react'
import { Button } from './ui/Button'

interface PreviewWindowProps {
  url?: string
}

export function PreviewWindow({ url }: PreviewWindowProps) {
  const defaultUrl = url || 'about:blank'
  const [iframeKey, setIframeKey] = useState(0)
  const [isLoading, setIsLoading] = useState(true)

  const handleRefresh = () => {
    setIframeKey((prev) => prev + 1)
    setIsLoading(true)
  }

  useEffect(() => {
    setIsLoading(true)
  }, [defaultUrl])

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
          key={iframeKey}
          src={defaultUrl}
          className="w-full h-full border-0"
          title="Preview"
          onLoad={() => setIsLoading(false)}
          sandbox="allow-same-origin allow-scripts allow-forms allow-popups allow-modals"
        />
      </div>
    </div>
  )
}

