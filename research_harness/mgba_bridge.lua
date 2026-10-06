-- mGBA 0.10.x bridge template. Session literals are inserted outside Git.
local host = "@@HOST@@"
local port = @@PORT@@
local token = "@@TOKEN@@"
local working_save = "@@SAVE@@"
local artifact_dir = "@@ARTIFACT_DIR@@"
local conn, err = socket.connect(host, port)
if not conn then error("harness connection: " .. tostring(err)) end
local buffer = ""
local armed = nil
local created_states = {}
local max_line = 256
local pending_frames = 0

local function reply(value)
    local payload = value .. "\n"
    local sent = conn:send(payload)
    if not sent or sent ~= #payload then error("harness send failed") end
end

local function number(s)
    if not s or not s:match("^%d+$") then return nil end
    return tonumber(s)
end

local function ram(address, width)
    return (address >= 0x02000000 and address + width <= 0x02040000)
        or (address >= 0x03000000 and address + width <= 0x03008000)
end

local function hex(bytes)
    return (bytes:gsub(".", function(c) return string.format("%02x", string.byte(c)) end))
end

local function dispatch(line)
    local fields = {}
    for field in (line .. "\t"):gmatch("([^\t]*)\t") do fields[#fields + 1] = field end
    local op = fields[1]
    local a, b = number(fields[2]), number(fields[3])
    if op == "health" and #fields == 1 then return "ok\t1" end
    if op == "meta" and #fields == 1 then
        return "ok\t" .. tostring(emu:platform()) .. "\t" .. emu:getGameTitle() .. "\t" .. emu:getGameCode()
    end
    if (op == "read8" or op == "read16" or op == "read32") and #fields == 2 then
        local width = ({read8=1, read16=2, read32=4})[op]
        if not a or not ram(a, width) then return "error\taddress" end
        return "ok\t" .. tostring(emu[op](emu, a))
    end
    if op == "read_range" and #fields == 3 then
        if not a or not b or b < 1 or b > 512 or not ram(a, b) then return "error\trange" end
        return "ok\t" .. hex(emu:readRange(a, b))
    end
    if op == "get_keys" and #fields == 1 then return "ok\t" .. tostring(emu:getKeys()) end
    if op == "set_keys" and #fields == 2 then
        if not a or a > 1023 then return "error\tkeys" end
        emu:setKeys(a)
        return "ok\t" .. tostring(emu:getKeys())
    end
    if op == "frames" and #fields == 2 then
        if not a or a < 1 or a > 120 then return "error\tframes" end
        if pending_frames ~= 0 then return "error\tbusy" end
        pending_frames = a
        return nil
    end
    if (op == "screenshot" or op == "save_state" or op == "load_state") and #fields == 2 then
        if not a or a < 1 or a > 99 then return "error\tartifact" end
        local path = artifact_dir .. "/" .. (op == "screenshot" and "screen-" or "state-") .. a .. (op == "screenshot" and ".png" or ".ss0")
        if op == "screenshot" then emu:screenshot(path); return "ok\t" .. tostring(a) end
        if op == "save_state" then
            if emu:saveStateFile(path) then created_states[a] = true; return "ok\t1" end
            return "error\tstate"
        end
        if not created_states[a] then return "error\tstate" end
        return emu:loadStateFile(path) and "ok\t1" or "error\tstate"
    end
    if op == "load_save" and #fields == 1 then
        return emu:loadSaveFile(working_save, false) and "ok\t1" or "error\tsave"
    end
    if op == "reset" and #fields == 1 then
        emu:reset()
        return "ok\t1"
    end
    if op == "arm_money" and #fields == 3 then
        if not a or not b or not ram(a, 4) or a % 4 ~= 0 or armed then return "error\tarm" end
        if emu:read32(a) ~= b then return "error\tbefore" end
        armed = a
        return "ok\t1"
    end
    local width = ({write8=1, write16=2, write32=4})[op]
    if width and #fields == 3 then
        if not a or not b or not armed or a < armed or a + width > armed + 4
            or not ram(a, width) or a % width ~= 0 or b >= 2^(8*width) then return "error\twrite" end
        emu[op](emu, a, b)
        return "ok\t" .. tostring(emu["read" .. (width * 8)](emu, a))
    end
    return "error\tcommand"
end

conn:add("received", function()
    local chunk = conn:receive(4096)
    if not chunk then error("harness disconnected") end
    buffer = buffer .. chunk
    if #buffer > max_line and not buffer:find("\n", 1, true) then error("harness request too large") end
    while true do
        local pos = buffer:find("\n", 1, true)
        if not pos then break end
        local line = buffer:sub(1, pos - 1)
        buffer = buffer:sub(pos + 1)
        if #line > max_line then error("harness request too large") end
        local result = dispatch(line)
        if result then reply(result) end
    end
end)
callbacks:add("frame", function()
    if pending_frames > 0 then
        pending_frames = pending_frames - 1
        if pending_frames == 0 then reply("ok\t1") end
    end
end)
reply("hello\t" .. token)
