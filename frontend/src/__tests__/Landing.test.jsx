import { render, screen } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import { describe, it, expect } from 'vitest'
import Landing from '../pages/Landing'

describe('Landing page', () => {
  it('renders without crashing', () => {
    render(
      <BrowserRouter>
        <Landing />
      </BrowserRouter>
    )
    expect(screen.getAllByText(/Sentra/).length).toBeGreaterThanOrEqual(1)
  })

  it('shows 13 attack types in hero section', () => {
    render(
      <BrowserRouter>
        <Landing />
      </BrowserRouter>
    )
    expect(screen.getByText(/13 attack types/i)).toBeTruthy()
  })

  it('has Start Free Audit button', () => {
    render(
      <BrowserRouter>
        <Landing />
      </BrowserRouter>
    )
    expect(screen.getAllByText('Start Free Audit').length).toBeGreaterThanOrEqual(1)
  })
})
