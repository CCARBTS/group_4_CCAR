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
      setRaw(JSON.stringify(parsed, null, 2));
    } catch (error) {
      setAnswer("Error: " + error.message);
    }
  };

  const renderTable = (data) => {
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

  return (
    <div>
      <h2>Ask about the data</h2>
      <input value={question} onChange={e => setQuestion(e.target.value)} />
      <button onClick={handleAsk}>Ask</button>

      <div style={{ marginTop: '1rem' }}>
        {answer ? renderTable(answer) : <p>No answer yet.</p>}
      </div>

      {/* Optional: raw output for debugging */}
      <pre style={{ background: "#f4f4f4", padding: "1em" }}>{raw}</pre>
    </div>
  );
}

export default PandasAIChat;

