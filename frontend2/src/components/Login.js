import React, { useState } from "react";
import { useNavigate } from "react-router-dom";

function Login() {
  const [opcode, setOpCode] = useState("");
  const [dni, setDni] = useState("");
  const navigate = useNavigate();

  const handleLogin = async () => {
    const res = await fetch("http://localhost:8000/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ opcode, dni })
    });
    const data = await res.json();
    if (data.status === "success") {
      navigate("/reports");
    } else {
      alert("Credenciales inválidas");
    }
  };

  return (
    <div className="container">
      <h2>Login Administrador</h2>
      <input placeholder="opcode" value={opcode} onChange={e => setOpCode(e.target.value)} />
      <input placeholder="DNI" value={dni} onChange={e => setDni(e.target.value)} />
      <button onClick={handleLogin}>Ingresar</button>
    </div>
  );
}

export default Login;