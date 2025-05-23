import React, { useState, useEffect } from "react";

export default function FileManager() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [userRole, setUserRole] = useState(null);
  const [fileName, setFileName] = useState("");
  const [fileContent, setFileContent] = useState("");
  const [selectedFile, setSelectedFile] = useState("");
  const [fileList, setFileList] = useState([]);
  const [message, setMessage] = useState("");
  const [isCompressed, setIsCompressed] = useState(false);

  // Simple RLE compression algorithm
  const compressContent = (text) => {
    if (!text) return "";
    let compressed = "";
    let count = 1;
    for (let i = 0; i < text.length; i++) {
      if (text[i] === text[i + 1]) {
        count++;
      } else {
        compressed += count > 1 ? `${count}${text[i]}` : text[i];
        count = 1;
      }
    }
    return compressed;
  };

  // Decompress RLE encoded text
  const decompressContent = (text) => {
    if (!text) return "";
    let decompressed = "";
    let count = "";
    
    for (let i = 0; i < text.length; i++) {
      if (!isNaN(text[i])) {
        count += text[i];
      } else {
        const repeat = count ? parseInt(count) : 1;
        decompressed += text[i].repeat(repeat);
        count = "";
      }
    }
    return decompressed;
  };

  useEffect(() => {
    const keys = Object.keys(localStorage).filter(key => !key.endsWith('_compressed'));
    setFileList(keys);
  }, []);

  const login = () => {
    if (username === "admin" && password === "admin123") {
      setUserRole("admin");
      setMessage("");
    } else if (username === "normal" && password === "user123") {
      setUserRole("normal");
      setMessage("");
    } else {
      setMessage("Invalid credentials.");
    }
  };

  const createFile = () => {
    if (!fileName) return setMessage("Please enter a file name.");
    if (localStorage.getItem(fileName)) return setMessage("File already exists.");
    localStorage.setItem(fileName, "");
    setFileList([...fileList, fileName]);
    setMessage(`File '${fileName}' created.`);
  };

  const writeFile = () => {
    if (!fileName) return setMessage("Please enter a file name.");
    const contentToWrite = isCompressed ? compressContent(fileContent) : fileContent;
    localStorage.setItem(fileName, contentToWrite);
    localStorage.setItem(`${fileName}_compressed`, isCompressed.toString());
    if (!fileList.includes(fileName)) setFileList([...fileList, fileName]);
    setMessage(`Content written to '${fileName}' ${isCompressed ? '(compressed)' : ''}.`);
  };

  const readFile = () => {
    if (!selectedFile) return setMessage("Please select a file to read.");
    const content = localStorage.getItem(selectedFile);
    const wasCompressed = localStorage.getItem(`${selectedFile}_compressed`) === "true";
    const displayContent = wasCompressed ? decompressContent(content) : content;
    setFileContent(displayContent);
    setFileName(selectedFile);
    setIsCompressed(wasCompressed);
    setMessage(`Reading '${selectedFile}' ${wasCompressed ? '(compressed)' : ''}.`);
  };

  const deleteFile = () => {
    if (!selectedFile) return setMessage("Please select a file to delete.");
    localStorage.removeItem(selectedFile);
    localStorage.removeItem(`${selectedFile}_compressed`);
    setFileList(fileList.filter(f => f !== selectedFile));
    setSelectedFile("");
    setFileContent("");
    setFileName("");
    setIsCompressed(false);
    setMessage(`File '${selectedFile}' deleted.`);
  };

  if (!userRole) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-100">
        <div className="bg-white p-6 rounded shadow-md w-full max-w-md">
          <h2 className="text-xl font-semibold text-center mb-4">Login</h2>
          <input
            type="text"
            placeholder="Username"
            className="w-full mb-2 p-2 border rounded text-black"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
          />
          <input
            type="password"
            placeholder="Password"
            className="w-full mb-4 p-2 border rounded text-black"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          <button
            onClick={login}
            className="w-full bg-blue-500 text-white py-2 rounded hover:bg-blue-600"
          >
            Login
          </button>
          {message && <p className="text-red-500 text-center mt-2">{message}</p>}
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <h1 className="text-2xl font-bold mb-4 text-black">File Management System</h1>
      <p className="mb-2">Logged in as: <strong>{userRole}</strong></p>

      <div className="max-w-xl space-y-4">
        <input
          type="text"
          placeholder="Enter file name"
          className="w-full p-2 border rounded text-black"
          value={fileName}
          onChange={(e) => setFileName(e.target.value)}
        />

        <textarea
          placeholder="Enter file content"
          className="w-full p-2 border rounded h-32 text-black"
          value={fileContent}
          onChange={(e) => setFileContent(e.target.value)}
        />

        {userRole === "admin" && (
          <>
            <div className="flex items-center gap-2 mb-2">
              <input
                type="checkbox"
                id="compress"
                checked={isCompressed}
                onChange={(e) => setIsCompressed(e.target.checked)}
                className="form-checkbox h-5 w-5 text-blue-600"
              />
              <label htmlFor="compress" className="text-black">Compress file content</label>
            </div>
            <button onClick={createFile} className="w-full bg-green-500 text-white py-2 rounded hover:bg-green-600">Create File</button>
            <button onClick={writeFile} className="w-full bg-yellow-500 text-white py-2 rounded hover:bg-yellow-600">
              {isCompressed ? 'Write & Compress File' : 'Write to File'}
            </button>
            <button onClick={deleteFile} className="w-full bg-red-500 text-white py-2 rounded hover:bg-red-600">Delete File</button>
          </>
        )}

        <div>
          <select
            className="w-full p-2 border rounded text-black border-black"
            value={selectedFile}
            onChange={(e) => setSelectedFile(e.target.value)}
          >
            <option value="" className="text-black border border-black">Select a file</option>
            {fileList.map((file, index) => (
              <option key={index} value={file}>
                {file} {localStorage.getItem(`${file}_compressed`) === "true" ? "(Compressed)" : ""}
              </option>
            ))}
          </select>
          <button 
            onClick={readFile} 
            className="w-full mt-2 bg-indigo-500 text-white py-2 rounded hover:bg-indigo-600"
            disabled={userRole === "normal" && !localStorage.getItem(`${selectedFile}_compressed`)}
          >
            Read File
          </button>
        </div>

        <button onClick={() => window.location.reload()} className="w-full border py-2 rounded hover:bg-gray-100">Logout</button>

        {message && <p className="text-green-600 mt-2">{message}</p>}

        {fileContent && (
          <div className="mt-6 p-4 border rounded bg-white">
            <h3 className="font-semibold">File Content:</h3>
            <pre className="whitespace-pre-wrap">{fileContent}</pre>
          </div>
        )}
      </div>
    </div>
  );
}