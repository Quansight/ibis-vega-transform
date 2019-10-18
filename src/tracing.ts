const SERVER_URL = 'http://localhost:8000';

async function callServer(path: string, data: object): Promise<any> {
  const response = await fetch(`${SERVER_URL}/${path}`, {
    body: JSON.stringify(data),
    method: 'POST',
    mode: 'cors',
    headers: {
      'Content-Type': 'application/json'
    }
  });
  return await response.json();
}

export async function startSpanExtract(data: {
  name: string;
  reference: object;
  relationship: 'child_of' | 'follows_from';
}): Promise<{ id: string }> {
  return callServer('start-span-extract', data);
}

export async function startSpan(data: {
  name: string;
  reference: { id: string };
  relationship: 'child_of' | 'follows_from';
}): Promise<{ id: string }> {
  return callServer('start-span', data);
}

export async function injectSpan(data: { id: string }): Promise<object> {
  return callServer('inject-span', data);
}

export async function finishSpan(data: { id: string }): Promise<void> {
  await callServer('finish-span', data);
  return;
}
