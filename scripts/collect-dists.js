#!/usr/bin/env node
"use strict";

const fs = require("node:fs/promises");
const path = require("node:path");

const DESTINATION_DIR_NAME = "libraries-dist";
const DIST_DIR_NAME = "dist";
const IGNORED_DIRS = new Set([
  "node_modules",
  ".git",
  ".next",
  "build",
  DESTINATION_DIR_NAME,
]);

function printUsage() {
  console.log(`
Usage:
  node scripts/collect-dists.js --copy [--clean]
  node scripts/collect-dists.js --move [--clean]

Options:
  --copy    Copy discovered dist folders into libraries-dist
  --move    Move discovered dist folders into libraries-dist
  --clean   Delete existing libraries-dist before collecting
  --help    Show this help message
`);
}

function parseArgs(argv) {
  const args = new Set(argv);
  const copy = args.has("--copy");
  const move = args.has("--move");

  if (args.has("--help") || args.has("-h")) {
    return { help: true };
  }

  if (copy === move) {
    throw new Error("Choose exactly one operation: --copy or --move.");
  }

  const unsupported = argv.filter(
    (arg) => !["--copy", "--move", "--clean", "--help", "-h"].includes(arg),
  );
  if (unsupported.length > 0) {
    throw new Error(`Unsupported option(s): ${unsupported.join(", ")}`);
  }

  return {
    clean: args.has("--clean"),
    operation: copy ? "copy" : "move",
  };
}

async function pathExists(targetPath) {
  try {
    await fs.access(targetPath);
    return true;
  } catch {
    return false;
  }
}

async function removeIfExists(targetPath) {
  if (await pathExists(targetPath)) {
    await fs.rm(targetPath, { recursive: true, force: true });
  }
}

async function scanForDistFolders(rootDir) {
  const discovered = [];

  async function walk(currentDir) {
    let entries;
    try {
      entries = await fs.readdir(currentDir, { withFileTypes: true });
    } catch (error) {
      console.warn(`[warn] Skipping unreadable directory: ${currentDir}`);
      console.warn(`       ${error.message}`);
      return;
    }

    for (const entry of entries) {
      if (!entry.isDirectory()) {
        continue;
      }

      if (IGNORED_DIRS.has(entry.name)) {
        continue;
      }

      const childPath = path.join(currentDir, entry.name);

      if (entry.name === DIST_DIR_NAME) {
        discovered.push(childPath);
        // A dist directory is an output artifact; do not recurse into it.
        continue;
      }

      await walk(childPath);
    }
  }

  await walk(rootDir);
  return discovered;
}

async function directorySizeBytes(dirPath) {
  let total = 0;

  async function walk(currentDir) {
    let entries;
    try {
      entries = await fs.readdir(currentDir, { withFileTypes: true });
    } catch (error) {
      console.warn(`[warn] Could not size directory: ${currentDir}`);
      console.warn(`       ${error.message}`);
      return;
    }

    for (const entry of entries) {
      const childPath = path.join(currentDir, entry.name);
      if (entry.isDirectory()) {
        await walk(childPath);
      } else if (entry.isFile()) {
        const stat = await fs.stat(childPath);
        total += stat.size;
      }
    }
  }

  await walk(dirPath);
  return total;
}

function inferLibraryName(distPath, rootDir) {
  const parentDir = path.dirname(distPath);
  const libraryName = path.basename(parentDir);
  const parentGroupName = path.basename(path.dirname(parentDir));
  const relativePath = path.relative(rootDir, distPath);

  return {
    libraryName,
    parentGroupName,
    relativePath,
  };
}

function buildDestinationNames(distFolders, rootDir) {
  const counts = new Map();
  const metadata = distFolders.map((distPath) => inferLibraryName(distPath, rootDir));

  for (const item of metadata) {
    counts.set(item.libraryName, (counts.get(item.libraryName) || 0) + 1);
  }

  const usedNames = new Set();
  return metadata.map((item) => {
    let destinationName = item.libraryName;

    if (counts.get(item.libraryName) > 1) {
      destinationName = `${item.parentGroupName}-${item.libraryName}`;
    }

    // If the parent-name strategy still collides, append a stable numeric suffix.
    let uniqueName = destinationName;
    let suffix = 2;
    while (usedNames.has(uniqueName)) {
      uniqueName = `${destinationName}-${suffix}`;
      suffix += 1;
    }
    usedNames.add(uniqueName);

    return {
      ...item,
      destinationName: uniqueName,
    };
  });
}

async function copyOrMoveDirectory(sourcePath, destinationPath, operation) {
  await removeIfExists(destinationPath);
  await fs.mkdir(path.dirname(destinationPath), { recursive: true });

  if (operation === "copy") {
    await fs.cp(sourcePath, destinationPath, {
      recursive: true,
      errorOnExist: false,
      force: true,
    });
    return;
  }

  try {
    await fs.rename(sourcePath, destinationPath);
  } catch (error) {
    if (error.code !== "EXDEV") {
      throw error;
    }

    // Cross-device moves cannot be renamed atomically, so copy then remove.
    await fs.cp(sourcePath, destinationPath, {
      recursive: true,
      errorOnExist: false,
      force: true,
    });
    await fs.rm(sourcePath, { recursive: true, force: true });
  }
}

function formatBytes(bytes) {
  if (bytes === 0) {
    return "0 B";
  }

  const units = ["B", "KB", "MB", "GB", "TB"];
  const index = Math.min(Math.floor(Math.log(bytes) / Math.log(1024)), units.length - 1);
  const value = bytes / 1024 ** index;
  return `${value.toFixed(value >= 10 || index === 0 ? 0 : 1)} ${units[index]}`;
}

async function main() {
  const options = parseArgs(process.argv.slice(2));
  if (options.help) {
    printUsage();
    return;
  }

  const rootDir = process.cwd();
  const destinationRoot = path.join(rootDir, DESTINATION_DIR_NAME);

  console.log("Dist Collector");
  console.log("==============");
  console.log(`Root:        ${rootDir}`);
  console.log(`Operation:   ${options.operation}`);
  console.log(`Destination: ${destinationRoot}`);

  if (options.clean) {
    console.log(`Cleaning existing ${DESTINATION_DIR_NAME}...`);
    await removeIfExists(destinationRoot);
  }

  const distFolders = await scanForDistFolders(rootDir);
  const destinationNames = buildDestinationNames(distFolders, rootDir);
  await fs.mkdir(destinationRoot, { recursive: true });

  let totalBytes = 0;
  let completed = 0;

  for (let index = 0; index < distFolders.length; index += 1) {
    const sourcePath = distFolders[index];
    const destinationPath = path.join(destinationRoot, destinationNames[index].destinationName);
    const size = await directorySizeBytes(sourcePath);

    try {
      await copyOrMoveDirectory(sourcePath, destinationPath, options.operation);
      totalBytes += size;
      completed += 1;
      console.log(
        `[ok] ${options.operation === "copy" ? "Copied" : "Moved"} ` +
          `${destinationNames[index].relativePath} -> ` +
          `${path.relative(rootDir, destinationPath)} (${formatBytes(size)})`,
      );
    } catch (error) {
      console.error(`[error] Failed to process ${sourcePath}`);
      console.error(`        ${error.message}`);
    }
  }

  console.log("");
  console.log("Summary");
  console.log("-------");
  console.log(`Total dist folders found: ${distFolders.length}`);
  console.log(`Successfully ${options.operation === "copy" ? "copied" : "moved"}: ${completed}`);
  console.log(`Total size ${options.operation === "copy" ? "copied" : "moved"}: ${formatBytes(totalBytes)}`);
  console.log(`Destination path: ${destinationRoot}`);
}

main().catch((error) => {
  console.error("[fatal] Dist collection failed.");
  console.error(error.message);
  process.exitCode = 1;
});
