/**
 * API client for the Optimotion Service Desk backend.
 */

const API_BASE = '/api';

// ─── Conversations ───────────────────────────────────────────────────────────

export async function createConversation(vehicleId, issueDescription) {
  const res = await fetch(`${API_BASE}/conversations`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      vehicle_id: vehicleId,
      issue_description: issueDescription,
    }),
  });
  if (!res.ok) throw new Error(`Failed to create conversation: ${res.statusText}`);
  return res.json();
}

export async function listConversations() {
  const res = await fetch(`${API_BASE}/conversations`);
  if (!res.ok) throw new Error(`Failed to list conversations: ${res.statusText}`);
  return res.json();
}

export async function getConversation(id) {
  const res = await fetch(`${API_BASE}/conversations/${id}`);
  if (!res.ok) throw new Error(`Failed to get conversation: ${res.statusText}`);
  return res.json();
}

/**
 * Send a message and stream the AI response.
 * @param {string} conversationId
 * @param {string} content
 * @param {(chunk: string) => void} onChunk — called for each streamed text chunk
 * @param {() => void} onDone — called when streaming is complete
 * @param {(error: string) => void} onError — called on error
 */
export async function sendMessage(conversationId, content, onChunk, onDone, onError) {
  try {
    const res = await fetch(`${API_BASE}/conversations/${conversationId}/messages`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ content }),
    });

    if (!res.ok) {
      onError?.(`Server error: ${res.statusText}`);
      return;
    }

    const reader = res.body.getReader();
    const decoder = new TextDecoder();

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const text = decoder.decode(value, { stream: true });
      // Parse SSE events (may contain multiple events in one chunk)
      const lines = text.split('\n');
      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const event = JSON.parse(line.slice(6));
            if (event.type === 'chunk') {
              onChunk?.(event.content);
            } else if (event.type === 'done') {
              onDone?.();
            } else if (event.type === 'error') {
              onError?.(event.content);
            }
          } catch {
            // Partial JSON, ignore
          }
        }
      }
    }

    // Ensure onDone is called even if no explicit done event was received
    onDone?.();
  } catch (err) {
    onError?.(err.message);
  }
}

export async function resolveConversation(id) {
  const res = await fetch(`${API_BASE}/conversations/${id}/resolve`, { method: 'POST' });
  if (!res.ok) throw new Error(`Failed to resolve conversation: ${res.statusText}`);
  return res.json();
}

export async function escalateConversation(id) {
  const res = await fetch(`${API_BASE}/conversations/${id}/escalate`, { method: 'POST' });
  if (!res.ok) throw new Error(`Failed to escalate conversation: ${res.statusText}`);
  return res.json();
}

// ─── Tickets ─────────────────────────────────────────────────────────────────

export async function listTickets() {
  const res = await fetch(`${API_BASE}/tickets`);
  if (!res.ok) throw new Error(`Failed to list tickets: ${res.statusText}`);
  return res.json();
}

export async function getTicket(id) {
  const res = await fetch(`${API_BASE}/tickets/${id}`);
  if (!res.ok) throw new Error(`Failed to get ticket: ${res.statusText}`);
  return res.json();
}

export async function updateTicket(id, data) {
  const res = await fetch(`${API_BASE}/tickets/${id}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error(`Failed to update ticket: ${res.statusText}`);
  return res.json();
}
