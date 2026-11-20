// One subscription to the babies, shared by every card on the page.

import type { Baby, HassConnection } from "./types";

type Listener = (babies: Baby[]) => void;

interface Subscription {
  babies: Baby[] | null;
  listeners: Set<Listener>;
  unsubscribe: Promise<() => Promise<void>> | null;
}

const subscriptions = new WeakMap<HassConnection, Subscription>();

/**
 * Call ``listener`` with the babies now (if known) and whenever they
 * change. Returns the function that stops listening; the subscription
 * itself ends when the last listener stops.
 */
export function watchBabies(connection: HassConnection, listener: Listener): () => void {
  let subscription = subscriptions.get(connection);
  if (!subscription) {
    const created: Subscription = { babies: null, listeners: new Set(), unsubscribe: null };
    created.unsubscribe = connection.subscribeMessage<{ babies: Baby[] }>(
      (message) => {
        created.babies = message.babies;
        created.listeners.forEach((each) => each(message.babies));
      },
      { type: "baby_calendar/subscribe_babies" },
    );
    subscriptions.set(connection, created);
    subscription = created;
  }
  const current = subscription;
  current.listeners.add(listener);
  if (current.babies) listener(current.babies);
  return () => {
    current.listeners.delete(listener);
    if (!current.listeners.size) {
      subscriptions.delete(connection);
      current.unsubscribe?.then((stop) => stop()).catch(() => undefined);
    }
  };
}
