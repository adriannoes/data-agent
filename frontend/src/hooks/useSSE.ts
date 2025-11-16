import { useEffect, useRef } from 'react'

interface SSEMessage {
  event: string
  data: any
}

export function useSSE(
  url: string | null,
  onMessage: (message: SSEMessage) => void,
  onError?: (error: Event) => void
) {
  const eventSourceRef = useRef<EventSource | null>(null)

  useEffect(() => {
    if (!url) {
      return
    }

    const eventSource = new EventSource(url)
    eventSourceRef.current = eventSource

    // Handle default message event
    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        onMessage({
          event: 'message',
          data,
        })
      } catch (error) {
        console.error('Error parsing SSE message:', error)
      }
    }

    // Handle custom named events (preview, status, complete, error)
    const eventTypes = ['preview', 'status', 'complete', 'error']
    eventTypes.forEach((eventType) => {
      eventSource.addEventListener(eventType, (event: any) => {
        try {
          const data = JSON.parse(event.data)
          onMessage({
            event: eventType,
            data,
          })
        } catch (error) {
          console.error(`Error parsing SSE ${eventType} event:`, error)
        }
      })
    })

    eventSource.onerror = (error) => {
      console.error('SSE error:', error)
      if (onError) {
        onError(error)
      }
    }

    return () => {
      eventSource.close()
    }
  }, [url, onMessage, onError])

  const close = () => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close()
      eventSourceRef.current = null
    }
  }

  return { close }
}

