import { describe, it, expect, vi } from 'vitest';
import { createSession, advanceSession, getSession } from './tarot-api';

const mockFetch = vi.fn();
global.fetch = mockFetch;

describe('tarot-api', () => {
  beforeEach(() => {
    mockFetch.mockReset();
  });

  it('createSession calls POST /api/tarot/session', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ session_id: 'abc', phase: 'ritual' }),
    });

    const result = await createSession();

    expect(mockFetch).toHaveBeenCalledWith(
      expect.stringContaining('/api/tarot/session'),
      expect.objectContaining({ method: 'POST' }),
    );
    expect(result.session_id).toBe('abc');
  });

  it('advanceSession sends action payload', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ session_id: 'abc', phase: 'reveal' }),
    });

    await advanceSession('abc', { kind: 'set_intention', text: 'hello' });

    const [, options] = mockFetch.mock.calls[0];
    const body = JSON.parse(options.body as string);
    expect(body.kind).toBe('set_intention');
    expect(body.text).toBe('hello');
  });

  it('getSession fetches current state', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ session_id: 'abc', phase: 'reveal' }),
    });

    const result = await getSession('abc');
    expect(result.phase).toBe('reveal');
  });
});
