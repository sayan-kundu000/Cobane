import React, { useState } from 'react';
import MonacoWrapper from '../components/monaco/MonacoWrapper.tsx';

export const Reviews: React.FC = () => {
  const [code, setCode] = useState<string>(
    'def calculate_sum(a, b):\n    # TODO: validate input variables\n    result = a + b\n    return result\n'
  );

  return (
    <div className="space-y-6">
      <div className="bg-white p-6 rounded-lg shadow dark:bg-gray-800">
        <h1 className="text-2xl font-bold mb-2">Interactive Code Review Console</h1>
        <p className="text-gray-600 dark:text-gray-300">Inspect suggested refactor changes and complexity index below.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div>
          <h3 className="text-lg font-medium mb-2">Editor Panel</h3>
          <MonacoWrapper code={code} onChange={(val) => setCode(val || '')} />
        </div>
        <div className="p-6 bg-white rounded-lg shadow dark:bg-gray-800 space-y-4">
          <h3 className="text-lg font-bold">Review Findings</h3>
          <div className="p-4 bg-yellow-50 text-yellow-800 rounded border border-yellow-200 text-sm">
            <strong>Naming suggestion:</strong> Consider renaming <code>result</code> to a more descriptive variable.
          </div>
        </div>
      </div>
    </div>
  );
};
export default Reviews;
