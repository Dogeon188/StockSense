function isClient() {
    return typeof window !== 'undefined' && typeof document !== 'undefined';
}

// prevent server side rendering from crashing
export function ClientOnly(target: any, ctx: DecoratorContext) {
    if (isClient()) return target;
    if (ctx.kind === 'method') {
        return function () {};
    }
    return;
}
