console.log('test_module loaded')

importScripts("https://cdn.jsdelivr.net/pyodide/v0.28.0/pyc/pyodide.js");

/*
importScripts("https://cdn.jsdelivr.net/npm/@zarrita/storage/fetch/+esm");
importScripts("https://cdn.jsdelivr.net/npm/zarrita/+esm");

importScripts("https://cdn.jsdelivr.net/npm/fast-xml-parser/+esm");

async function main() {
const url = 'https://storage.googleapis.com/brim-example-files/drosophila_LSBM.brim.zarr'

let store = new FetchStore(url)
let root = await zarrita.open.v3(store, { kind: "group" });

function standardize_path(path) {
  if (!path.endsWith('/')) {
    path = path + '/';
  }
  if (path.startsWith('/')) {
    path = path.slice(1);
  }
  return path;
}

async function list_S3keys(store_url, full_path){

    function split_path(url, full_path) {
      url = standardize_path(url).slice(0,-1);
      full_path = standardize_path(full_path);

      let path = [];
      const last_slash = url.lastIndexOf('/');
      path.endpoint = url.slice(0, last_slash+1)
      path.object = url.slice(last_slash+1) + '/' + full_path
      return path;
    }
    const path = split_path(store_url, full_path);

    let queries = "list-type=2&delimiter=/";
    queries += "&prefix="+path.object;

    let url = path.endpoint + "?" + queries;
    url = encodeURI(url);

    const response = await fetch(url);
    if (!response.ok) throw new Error(`HTTP error: ${response.status}`);
    const xmlText = await response.text();

    // Parse XML using fast-xml-parser
    const parser = new XMLParser();
    const xmlObj = parser.parse(xmlText);

    function ExtractKeyFromPrefix (x) {
        let p = x.Prefix;
        if (p.endsWith('/')) {
            p = p.slice(0, -1)
        }
        p = p.split('/').pop()
        return p;
    }
    // Extract CommonPrefixes
    let prefixes = [];
    if (xmlObj.ListBucketResult && xmlObj.ListBucketResult.CommonPrefixes) {
        const cp = xmlObj.ListBucketResult.CommonPrefixes;
        if (Array.isArray(cp)) {
            prefixes = cp.map(ExtractKeyFromPrefix);
        } else if (cp.Prefix) {
            prefixes = [ExtractKeyFromPrefix(cp.Prefix)];
        }
    }
    return prefixes;
  }
let res = await list_S3keys( store.url, 'Brillouin_data/Data_0/Analysis_0')
console.log(res)
}
*/
async function startApplication() {
  self.pyodide = await loadPyodide();
  let result = await pyodide.runPythonAsync(`
      import asyncio     
      import js 
      async def _awaitable_wrapper(coro):
          return await coro

      def run_until_complete(coro):
          """
          Drop-in replacement for asyncio.get_event_loop().run_until_complete(coro)
          that works inside Pyodide (Web Worker or main thread).
          """
          loop = asyncio.get_event_loop()
          task = loop.create_task(_awaitable_wrapper(coro))
          # In Pyodide, we can't block the event loop, so instead we yield back
          # control until the task is done.
          while not task.done():
              loop.run_until_complete(asyncio.sleep(0))
          return task.result()

      async def hello(time=1):
        await asyncio.sleep(time)
        return f"Slept for {time} seconds"

      h1 = hello(1)
      h2 = hello(1.5)
      import time
      start = time.time()
      result = run_until_complete(asyncio.gather(h1, h2))   
      end = time.time()
      js.console.log(f"Elapsed time: {end - start} seconds")   
      js.console.log(result[0])
      js.console.log(result[1])
  `);
}
startApplication();