'use client'

import { useEffect, useRef, useCallback } from 'react'
import type { SSEEvent } from './types'

type SSEEventHandler = (event: SSEEvent) => void

interface UseSSEOptions {
  onOpen?: () => void
}

export function useSSE(
  url: string | null,
  onEvent: SSEEventHandler,
  options?: UseSSEOptions,
) {
  const eventSourceRef = useRef<EventSource | null>(null)
  const onEventRef = useRef(onEvent)
  const onOpenRef = useRef(options?.onOpen)

  useEffect(() => {
    onEventRef.current = onEvent
  }, [onEvent])

  useEffect(() => {
    onOpenRef.current = options?.onOpen
  }, [options?.onOpen])

  useEffect(() => {
    if (!url) return

    const eventSource = new EventSource(url)
    eventSourceRef.current = eventSource

    eventSource.onopen = () => {
      onOpenRef.current?.()
    }

    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data) as SSEEvent
        onEventRef.current(data)
      } catch (e) {
        console.error('Failed to parse SSE event:', e)
      }
    }

    eventSource.onerror = () => {
      eventSource.close()
    }

    return () => {
      eventSource.close()
      eventSourceRef.current = null
    }
  }, [url])

  const close = useCallback(() => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close()
      eventSourceRef.current = null
    }
  }, [])

  return { close }
}
