export async function uploadAttachment({ baseUrl, token, taskID, fileName, filePath, priority, tags }) {
	// baseUrl example: https://{apiId}.execute-api.us-east-1.amazonaws.com/dev
	const res = await fetch(`${baseUrl}/tasks/${encodeURIComponent(taskID)}/attachments/upload`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
			...(token ? { Authorization: token } : {})
		},
		body: JSON.stringify({ fileName, filePath, priority, tags })
	});
	if (!res.ok) {
		const text = await res.text();
		throw new Error(text || `Upload failed (${res.status})`);
	}
	return res.json();
}