// 最小 preload 桥：当前前端用相对路径 fetch 直接打本地 server，
// 不需要 node 集成。此处仅预留安全通道，后续如需调用原生能力再扩展。
const { contextBridge } = require("electron");

contextBridge.exposeInMainWorld("nexusdeck", {
  platform: process.platform,
  version: require("./package.json").version,
});
