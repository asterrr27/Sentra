import { Component } from 'react'

export default class ErrorBoundary extends Component {
  constructor(props) {
    super(props)
    this.state = { hasError: false }
  }

  static getDerivedStateFromError() {
    return { hasError: true }
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen flex items-center justify-center bg-[#09090B] px-4">
          <div className="text-center max-w-md">
            <div className="text-4xl mb-4">⚠️</div>
            <h1 className="text-xl font-bold mb-2">Something went wrong</h1>
            <p className="text-sm text-white/40 mb-6">An unexpected error occurred. Please try refreshing the page.</p>
            <button
              onClick={() => { this.setState({ hasError: false }); window.location.href = '/' }}
              className="px-6 py-2.5 text-sm font-semibold text-[#09090B] bg-gradient-to-r from-primary to-secondary rounded-full hover:shadow-lg hover:shadow-primary/20 transition-all"
            >
              Go Home
            </button>
          </div>
        </div>
      )
    }
    return this.props.children
  }
}
