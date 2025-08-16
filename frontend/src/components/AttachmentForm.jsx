import React, { useState } from 'react';

export default function AttachmentForm({ onSubmit, initialTaskID = '' }) {
	const [taskID, setTaskID] = useState(initialTaskID);
	const [fileName, setFileName] = useState('');
	const [filePath, setFilePath] = useState('');
	const [priority, setPriority] = useState('medium');
	const [tags, setTags] = useState(''); // comma-separated

	const submit = (e) => {
		e.preventDefault();
		onSubmit({
			taskID,
			fileName,
			filePath,
			priority,
			tags: tags ? tags.split(',').map(t => t.trim()).filter(Boolean) : []
		});
		setTaskID('');
		setFileName('');
		setFilePath('');
		setPriority('medium');
		setTags('');
	};

	return (
		<form onSubmit={submit}>
			<div>
				<label>Task ID</label>
				<input
					type="text"
					value={taskID}
					onChange={(e) => setTaskID(e.target.value)}
					required
				/>
			</div>
			<div>
				<label>File Name</label>
				<input
					type="text"
					value={fileName}
					onChange={(e) => setFileName(e.target.value)}
					required
				/>
			</div>
			<div>
				<label>File Path</label>
				<input
					type="text"
					value={filePath}
					onChange={(e) => setFilePath(e.target.value)}
					required
				/>
			</div>
			<div>
				<label>Priority</label>
				<select value={priority} onChange={(e) => setPriority(e.target.value)}>
					<option value="low">Low</option>
					<option value="medium">Medium</option>
					<option value="high">High</option>
				</select>
			</div>
			<div>
				<label>Tags (comma-separated)</label>
				<input value={tags} onChange={(e) => setTags(e.target.value)} placeholder="design, docs" />
			</div>
			<button type="submit">Upload</button>
		</form>
	);
}