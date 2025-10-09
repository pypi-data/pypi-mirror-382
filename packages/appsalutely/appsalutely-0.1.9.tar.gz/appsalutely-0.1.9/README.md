# appsalutely

A utility library for building apps with FastAPI and Vue.js.

[Python backend library](https://pypi.org/project/appsalutely)

[Vue.js frontend library](https://www.npmjs.com/package/appsalutely)

## Usage notes

For the frontend library to work correctly,
you will have to put the `peerDependencies` from the library's `package.json`
in your `vite.config.ts` under `resolve.dedupe`.
