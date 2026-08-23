const { app, BrowserWindow, ipcMain } = require("electron");
const { spawn } = require("child_process");
const path = require("path");
const net = require("net");
const fs = require("fs");

// 固定端口，Electron 窗口加载此地址
const PORT = 9600;
const HOST = "127.0.0.1";

let serverProc = null;
let mainWindow = null;

// 解析封进包内的 server 可执行路径
// PyInstaller onedir 产物：bin/nexusdeck-server/nexusdeck-server(.exe)
// 旧单文件产物：bin/nexusdeck-server(.exe)
function resolveServerBin() {
  if (!app.isPackaged) return null;
  const base = process.resourcesPath;
  const exeName = process.platform === "win32" ? "nexusdeck-server.exe" : "nexusdeck-server";

  // 优先 onedir 目录结构
  const onedirPath = path.join(base, "bin", "nexusdeck-server", exeName);
  if (fs.existsSync(onedirPath)) return onedirPath;

  // 兼容旧单文件结构
  const onefilePath = path.join(base, "bin", exeName);
  if (fs.existsSync(onefilePath)) return onefilePath;

  return onefilePath; // 返回默认值，让 spawn 时报错信息更明确
}

// 轮询端口是否就绪
function waitForPort(port, timeoutMs = 15000) {
  const start = Date.now();
  return new Promise((resolve, reject) => {
    const tryOnce = () => {
      const sock = net.connect(port, HOST);
      sock.once("connect", () => {
        sock.destroy();
        resolve(true);
      });
      sock.once("error", () => {
        sock.destroy();
        if (Date.now() - start > timeoutMs) {
          reject(new Error("server 端口等待超时"));
        } else {
          setTimeout(tryOnce, 300);
        }
      });
    };
    tryOnce();
  });
}

function startServer() {
  const bin = resolveServerBin();
  let proc;
  if (bin) {
    proc = spawn(bin, ["--no-browser", "--preferred-port", String(PORT)], {
      stdio: ["ignore", "pipe", "pipe"],
      env: { ...process.env, NEXUSDECK_DATA_DIR: app.getPath("userData") },
    });
  } else {
    // 开发模式：用系统 python 跑源码
    const py = process.env.NEXUSDECK_PYTHON || "python3";
    const src = path.join(__dirname, "..", "server.py");
    proc = spawn(py, [src, "--no-browser", "--preferred-port", String(PORT)], {
      stdio: ["ignore", "pipe", "pipe"],
    });
  }
  proc.stdout.on("data", (d) => process.stdout.write(`[server] ${d}`));
  proc.stderr.on("data", (d) => process.stderr.write(`[server:err] ${d}`));
  proc.on("exit", (code) => {
    if (code && code !== 0) console.error("server 进程退出:", code);
  });
  serverProc = proc;
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1280,
    height: 820,
    minWidth: 960,
    minHeight: 600,
    title: "NexusDeck",
    icon: path.join(__dirname, "assets", process.platform === "win32" ? "icon.ico" : "icon.icns"),
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      contextIsolation: true,
      nodeIntegration: false,
    },
  });

  // 禁止打开外部浏览器，所有导航留在窗口内
  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    // 仅允许同域（本地 server）内部跳转
    if (url.startsWith(`http://${HOST}:${PORT}`)) return { action: "allow" };
    return { action: "deny" };
  });

  mainWindow.loadURL(`http://${HOST}:${PORT}/`);
  mainWindow.on("closed", () => (mainWindow = null));
}

app.whenReady().then(async () => {
  startServer();
  try {
    await waitForPort(PORT);
  } catch (e) {
    console.error(e.message);
  }
  createWindow();

  app.on("activate", () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on("window-all-closed", () => {
  if (serverProc) serverProc.kill();
  if (process.platform !== "darwin") app.quit();
});

app.on("before-quit", () => {
  if (serverProc) serverProc.kill("SIGTERM");
});
