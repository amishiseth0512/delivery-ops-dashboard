import { useState } from 'react'
import { askAssistant } from '../api'

export default function AIAssistant() {
  const [question, setQuestion] = useState('')
  const [answer, setAnswer] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  async function handleAsk() {
    const trimmed = question.trim()
    if (!trimmed) {
      setError('Please enter a question.')
      return
    }
    setError('')
    setAnswer('')
    setLoading(true)
    try {
      const res = await askAssistant(trimmed)
      setAnswer(res.answer)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="bg-white rounded-lg p-4 shadow-sm mb-6">
      <h2 className="text-lg font-bold mb-3">AI Operations Assistant</h2>
      <div className="flex gap-3">
        <input
          type="text"
          value={question}
          onChange={e => setQuestion(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && handleAsk()}
          placeholder="e.g. Which deliveries need attention?"
          className="flex-1 border rounded px-3 py-2 text-sm"
        />
        <button
          onClick={handleAsk}
          disabled={loading}
          className="text-sm bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 disabled:opacity-50 shrink-0"
        >
          {loading ? 'Asking...' : 'Ask'}
        </button>
      </div>

      {loading && (
        <div className="flex items-center gap-2 mt-3 text-sm text-gray-500">
          <div className="h-4 w-4 border-2 border-gray-300 border-t-blue-600 rounded-full animate-spin" />
          Thinking...
        </div>
      )}

      {error && <p className="text-red-500 text-sm mt-3">{error}</p>}

      {answer && !loading && (
        <p className="text-sm text-gray-700 mt-3 whitespace-pre-line">{answer}</p>
      )}
    </div>
  )
}
