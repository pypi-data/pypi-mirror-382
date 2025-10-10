# actor-header-component

The goal here is to provide a header component for actors, that works out
of the box. The expected input format is the result of the
[actor_to_header_info](https://bovine.codeberg.page/muck_out/reference/derived/#muck_out.derived.actor_to_header_info)
call converted to an object.

The header component is currently used in [moo](https://moo.bovine.social/)
with the inclusion using some browser script tags available
[here](https://codeberg.org/helge/moo/src/branch/main/moo/templates/index.html.j2).

## Development

### Building

```bash
npm run build
```

creates a new version of the content of dist.

```bash
npm version prerelease
npm publish --access public
```

tags a new prerelease and publishes it npm.

### Setting up to run tests

```bash
npm install
./node_modules/.bin/playwright install
```

then one can run tests via

```bash
npm test
```

### Testing looks

```bash
npm run dev
```