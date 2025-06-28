import React, { useState } from 'react';
import axios from 'axios';


function PandasAIChat_orig() {
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState('');

  const handleAsk = async () => {
    try {
      const res = await axios.post('http://localhost:3001/api/ask', { question });
      setAnswer(res.data.answer);
    } catch (error) {
      setAnswer("Error: " + error.message);
    }
  };

  return (
    <div>
      <h2>Ask about the data</h2>
      <input value={question} onChange={e => setQuestion(e.target.value)} />
      <button onClick={handleAsk}>Ask</button>
      <p><strong>Answer:</strong> {answer}</p>
    </div>
  );
}

function PandasAIChat() {
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState(null);
  const [raw, setRaw] = useState(''); // Optional: for debugging
  const [plotUrl, setPlotUrl] = useState(null);

  const handleAsk = async () => {
    try {
      const res = await axios.post('http://localhost:3001/api/ask', { question });

      // Attempt to parse if it's a JSON string
      let parsed = res.data.answer;
      if (typeof parsed === 'string') {
        try {
          parsed = JSON.parse(parsed);
        } catch (e) {
          // Not JSON string, use as plain text
        }
      }

      setAnswer(parsed);
      setPlotUrl(res.data.plot_url || null);
      setRaw(JSON.stringify(parsed, null, 2));
    } catch (error) {
      setAnswer("Error: " + error.message);
      setPlotUrl(null);
    }
  };

  const renderTable2 = (data) => {
    if (!Array.isArray(data) || data.length === 0 || typeof data[0] !== 'object') {
      return <p><strong>Answer:</strong> {JSON.stringify(data)}</p>;
    }

    const headers = Object.keys(data[0]);

    return (
      <table border="1">
        <thead>
          <tr>
            {headers.map((key) => (
              <th key={key}>{key}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((row, i) => (
            <tr key={i}>
              {headers.map((key) => (
                <td key={key}>{row[key]}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    );
  };

  const renderTable = (data) => {
    if (!Array.isArray(data) || data.length === 0 || typeof data[0] !== 'object') {
      return <p className="text-gray-700">{JSON.stringify(data)}</p>;
    }
  
    const headers = Object.keys(data[0]);
  
    return (
      <div className="overflow-x-auto">
        <table className="min-w-full border border-gray-300 shadow-sm rounded-md">
          <thead className="bg-gray-100">
            <tr>
              {headers.map((key) => (
                <th key={key} className="px-4 py-2 text-left font-semibold text-gray-600 border-b">
                  {key}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {data.map((row, i) => (
              <tr key={i} className={i % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                {headers.map((key) => (
                  <td key={key} className="px-4 py-2 border-b text-gray-800">
                    {row[key]}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  };
  
  return (


    <div className="max-w-6xl mx-auto p-6 bg-white shadow-lg rounded-xl">
      <h2 className="text-2xl font-bold text-gray-800 mb-4">Ask about CCAR data:</h2>

      <div className="flex gap-4 mb-6">
        <input
          type="text"
          value={question}
          onChange={e => setQuestion(e.target.value)}
          placeholder="Enter your question..."
          className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400"
        />
        <button
          onClick={handleAsk}
          className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
        >
          Ask
        </button>
      </div>

    <div style={{ marginTop: '1rem' }}>
    <h3>Answer:</h3>

        {plotUrl ? (
          <img
            src={plotUrl}
            alt="Generated Plot"
            style={{ maxWidth: '100%', marginTop: '1rem' }}
          />
        ) : answer ? (
          typeof answer === 'object' ? (
            renderTable(answer)
          ) : (
            <p>{answer}</p>
          )
        ) : null
        }
    </div>

    </div>

  );
}


export default PandasAIChat;
