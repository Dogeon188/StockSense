// prevent server side rendering from crashing
const storage =
    (typeof (window) !== 'undefined' && typeof (document) !== 'undefined') ?
        localStorage :
        null;

const userConfigs = new Map<string, string>();

function registerUserConfig(key: string, defaultValue: string) {
    if (!storage) return;
    const value = storage.getItem(key);
    if (!value) {
        storage.setItem(key, defaultValue);
        userConfigs.set(key, defaultValue);
    } else {
        userConfigs.set(key, value);
    }
}

export function getUserConfig(key: string) {
    return userConfigs.get(key);
}

export function setUserConfig(key: string, value: string) {
    if (!storage) return;
    userConfigs.set(key, value);
    storage.setItem(key, value);
}

registerUserConfig('apiUrl', 'http://localhost:8086');