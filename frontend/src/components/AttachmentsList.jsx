import React from 'react';

export default function AttachmentsList({ items = [] }) {
	return (
		<table>
			<thead>
				<tr>
					<th>File</th>
					<th>Priority</th>
					<th>Uploaded</th>
				</tr>
			</thead>
			<tbody>
				{items.map(it => (
					<tr key={it.fileID}>
						<td>{it.fileName}</td>
						<td>{it.priority || '-'}</td>
						<td>{it.uploadedAt}</td>
					</tr>
				))}
			</tbody>
		</table>
	);
}