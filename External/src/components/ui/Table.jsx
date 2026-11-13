import React from 'react';
import { cn } from '../../utils/cn';

export function Table({
  columns = [],
  data = [],
  keyField = 'id',
  emptyMessage = 'No data available',
  className = '',
}) {
  return (
    <div className={cn('w-full overflow-x-auto border border-border/80 rounded-lg bg-card', className)}>
      <table className="w-full text-left border-collapse text-sm">
        <thead>
          <tr className="border-b border-border/80 bg-deep/50 text-muted uppercase text-xs tracking-wider">
            {columns.map((col, idx) => (
              <th
                key={col.key || idx}
                className={cn('py-3.5 px-4 font-semibold', col.align === 'right' ? 'text-right' : 'text-left')}
              >
                {col.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-border/60">
          {data.length === 0 ? (
            <tr>
              <td colSpan={columns.length} className="py-8 text-center text-muted">
                {emptyMessage}
              </td>
            </tr>
          ) : (
            data.map((row, rowIdx) => (
              <tr key={row[keyField] || rowIdx} className="hover:bg-white/[0.02] transition-colors">
                {columns.map((col, colIdx) => (
                  <td
                    key={col.key || colIdx}
                    className={cn('py-3.5 px-4 text-foreground/90', col.align === 'right' ? 'text-right' : 'text-left')}
                  >
                    {col.render ? col.render(row[col.key], row, rowIdx) : row[col.key]}
                  </td>
                ))}
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
}

