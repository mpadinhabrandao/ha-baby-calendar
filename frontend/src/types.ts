// The parts of Home Assistant's frontend objects the cards use.

export interface HassEntity {
  entity_id: string;
  state: string;
  attributes: Record<string, any>;
  last_changed: string;
}

export interface HassConnection {
  subscribeMessage<T>(
    callback: (message: T) => void,
    message: Record<string, unknown>,
  ): Promise<() => Promise<void>>;
  sendMessagePromise<T>(message: Record<string, unknown>): Promise<T>;
}

export interface Hass {
  states: Record<string, HassEntity>;
  connection: HassConnection;
  locale?: { language: string };
  language?: string;
}

export interface Schedule {
  type: "none" | "times" | "interval";
  times?: string[];
  hours?: number;
}

export interface Medication {
  id: string;
  name: string;
  dose: string | null;
  schedule: Schedule;
  entities: Record<string, string>;
}

export interface Baby {
  entry_id: string;
  device_id: string;
  name: string;
  trackers: string[];
  medications: Medication[];
  entities: Record<string, string>;
}

export interface CardConfig {
  type: string;
  baby?: string;
  show_all?: boolean;
}

export interface FeedEntry {
  side: string | null;
  start: string;
  end: string | null;
}

export interface EventItem {
  event_id: string;
  tracker: string;
  time: string;
  end?: string | null;
  duration?: number | null;
  in_progress?: boolean;
  notes?: string | null;
  [field: string]: unknown;
}
