import { useState } from 'react'
import { ChatWindow } from './components/ChatWindow'
import { PreviewWindow } from './components/PreviewWindow'

function App() {
  const [sessionId, setSessionId] = useState<string | null>(null)

  return (
    <div className="h-screen w-screen flex overflow-hidden bg-background">
      {/* Chat Window - Left Side */}
      <div className="w-1/2 border-r border-border flex flex-col">
        <ChatWindow onSessionChange={setSessionId} />
      </div>

      {/* Preview Window - Right Side */}
      <div className="w-1/2 flex flex-col">
        <PreviewWindow sessionId={sessionId} />
      </div>
    </div>
  )
}

export default App

