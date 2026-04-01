import type { CacheEntryRecord } from "@/domain/models";

export interface CacheStore {
  get(scope: CacheEntryRecord["scope"], key: string): CacheEntryRecord | null;
  set(entry: CacheEntryRecord): void;
}

export class InMemoryCacheStore implements CacheStore {
  private readonly records = new Map<string, CacheEntryRecord>();

  private buildScopedKey(
    scope: CacheEntryRecord["scope"],
    key: string
  ): string {
    return `${scope}:${key}`;
  }

  public get(
    scope: CacheEntryRecord["scope"],
    key: string
  ): CacheEntryRecord | null {
    const record = this.records.get(this.buildScopedKey(scope, key));

    if (record === undefined) {
      return null;
    }

    if (Date.parse(record.expires_at) <= Date.now()) {
      this.records.delete(this.buildScopedKey(scope, key));
      return null;
    }

    return {
      ...record,
      payload: JSON.parse(JSON.stringify(record.payload)) as Record<string, unknown>
    };
  }

  public set(entry: CacheEntryRecord): void {
    this.records.set(this.buildScopedKey(entry.scope, entry.cache_key), {
      ...entry,
      payload: JSON.parse(JSON.stringify(entry.payload)) as Record<string, unknown>
    });
  }
}
