import { ChatWindow } from './components/ChatWindow'
import { PreviewWindow } from './components/PreviewWindow'

function App() {
  return (
    <div className="h-screen w-screen flex overflow-hidden bg-background">
      {/* Chat Window - Left Side */}
      <div className="w-1/2 border-r border-border flex flex-col">
        <ChatWindow />
      </div>

      {/* Preview Window - Right Side */}
      <div className="w-1/2 flex flex-col">
        <PreviewWindow />
      </div>
    </div>
  )
}

export default App

