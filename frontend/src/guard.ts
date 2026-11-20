// Drops a repeated tap of the same button within a short time.

export const REPEAT_MS = 3000;

export class RepeatGuard {
  private last = new Map<string, number>();

  /** Return true when the tap should go through, and note it. */
  allow(key: string, now: number = Date.now()): boolean {
    const previous = this.last.get(key);
    if (previous !== undefined && now - previous < REPEAT_MS) return false;
    this.last.set(key, now);
    return true;
  }
}
