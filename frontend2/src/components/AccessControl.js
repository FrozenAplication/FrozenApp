import React, { useState } from "react";

function AccessControl() {
  const [usuario_id, setUsuarioId] = useState("");
  const [accion, setAccion] = useState("ingreso");
  const [tipo, setTipo] = useState("");

  const handleAccess = async () => {
    const res = await fetch("http://localhost:8000/access", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ usuario_id: parseInt(usuario_id), accion, tipo })
    });
    const data = await res.json();
    alert(data.msg || "Acceso registrado");
  };

  return (
    <div className="container">
      <h2>Registro de Acceso</h2>
      <input placeholder="ID Usuario" value={usuario_id} onChange={e => setUsuarioId(e.target.value)} />
      <select value={accion} onChange={e => setAccion(e.target.value)}>
        <option value="ingreso">Ingreso</option>
        <option value="egreso">Egreso</option>
      </select>
      <input placeholder="Tipo (opcional)" value={tipo} onChange={e => setTipo(e.target.value)} />
      <button onClick={handleAccess}>Registrar</button>
    </div>
  );
}

export default AccessControl;