/** Strip markdown/noise from trend bullets for consistent UI display. */
export function normalizeTrendHighlight(raw: string, maxLen = 140): string {
  let text = raw.trim()
  text = text.replace(/```[\s\S]*?```/g, ' ')
  text = text.replace(/\*\*([^*]+)\*\*/g, '$1')
  text = text.replace(/\*([^*]+)\*/g, '$1')
  text = text.replace(/#+\s*/g, '')
  text = text.replace(/\[([^\]]+)\]\([^)]+\)/g, '$1')
  text = text.replace(/\s+/g, ' ').trim()

  const colonIdx = text.indexOf(': ')
  if (colonIdx > 0 && colonIdx < 80) {
    const tail = text.slice(colonIdx + 2)
    if (tail.length > 30) text = tail
  }

  const sentence = text.match(/^(.+?[.!?])(?:\s|$)/)?.[1] ?? text
  let cleaned = sentence.trim()

  if (cleaned.length > maxLen) {
    const cut = cleaned.slice(0, maxLen - 1).replace(/\s+\S*$/, '')
    cleaned = cut ? `${cut}…` : `${cleaned.slice(0, maxLen - 1)}…`
  }

  if (cleaned && cleaned[0] === cleaned[0].toLowerCase()) {
    cleaned = cleaned[0].toUpperCase() + cleaned.slice(1)
  }

  return cleaned
}
