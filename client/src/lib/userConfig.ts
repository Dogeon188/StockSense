import { ClientOnly } from "./utils";

export class UserConfig {
    static storage: Storage = undefined!;

    static configs = new Map<string, string>();

    @ClientOnly
    static init() {
        UserConfig.storage = window.localStorage;
    }

    @ClientOnly
    static get(key: string) {
        return UserConfig.configs.get(key);
    }

    @ClientOnly
    static set(key: string, value: string) {
        UserConfig.configs.set(key, value);
        UserConfig.storage.setItem(key, value);
    }

    @ClientOnly
    static register(key: string, defaultValue: string) {
        const value = UserConfig.storage.getItem(key);
        if (!value) {
            UserConfig.storage.setItem(key, defaultValue);
            UserConfig.configs.set(key, defaultValue);
        } else {
            UserConfig.configs.set(key, value);
        }
    }
}

UserConfig.init();
UserConfig.register('apiUrl', 'http://localhost:8086');