import { create } from "zustand";

const { createEventHandlingSlice } = Whitebox.utils;

const createFlightSessionControlSlice = (set, get) => ({
  isReady: false,
  activeFlightSession: null,
  activeKeyMoment: null,

  // During the session, we are tracking key moments separately from the flight
  // session to avoid unnecessary component rerenders when updating the list.
  // This will be used both for flying and playbacks
  sessionKeyMoments: [],

  setSessionKeyMoments: (keyMoments) => {
    const newValues = {
      sessionKeyMoments: keyMoments,
    };

    const activeKeyMoment = keyMoments.find((k) => k.ended_at === null);
    // If there is an active one, set it, tho otherwise we want null too
    newValues.activeKeyMoment = activeKeyMoment || null;

    set(newValues);
  },

  setActiveFlightSession: (session) => {
    const keyMoments = session?.key_moments || [];
    const activeKeyMoment = keyMoments.find((k) => k.ended_at === null);

    set({
      activeFlightSession: session,
      isReady: true,
      sessionKeyMoments: keyMoments,
      activeKeyMoment: activeKeyMoment,
    });
  },

  setActiveKeyMoment: (keyMoment) => {
    set({
      activeKeyMoment: keyMoment,
    });
  },

  getFlightSession: () => {
    return get().activeFlightSession;
  },

  isFlightSessionActive: () => {
    const flightSession = get().activeFlightSession;
    return flightSession && flightSession.ended_at === null;
  },

  isKeyMomentActive: () => {
    const keyMoment = get().activeKeyMoment;
    return keyMoment && keyMoment.ended_at === null;
  },

  // region entry management

  startFlightSession: async () => {
    set({ isReady: false });

    const data = {
      type: "flight.start",
    };
    Whitebox.sockets.send("flight", data);
  },

  endFlightSession: async () => {
    set({ isReady: false });

    const data = {
      type: "flight.end",
    };
    Whitebox.sockets.send("flight", data);
  },

  toggleFlightSession: async () => {
    const flightSession = get().activeFlightSession;

    if (flightSession && flightSession.ended_at === null) {
      await get().endFlightSession();
    } else {
      await get().startFlightSession();
    }
  },

  // endregion entry management

  // region key moment management

  recordKeyMoment: () => {
    const data = {
      type: "flight.key_moment.record",
    };
    Whitebox.sockets.send("flight", data);
  },
  finishKeyMoment: () => {
    const data = {
      type: "flight.key_moment.finish",
    };
    Whitebox.sockets.send("flight", data);
  },

  updateKeyMoment: (keyMomentId, updates) => {
    const data = {
      type: "flight.key_moment.update",
      key_moment_id: keyMomentId,
      ...updates,
    };
    Whitebox.sockets.send("flight", data);
  },
  deleteKeyMoment: (keyMomentId) => {
    const data = {
      type: "flight.key_moment.delete",
      key_moment_id: keyMomentId,
    };
    Whitebox.sockets.send("flight", data);
  },

  // endregion key moment management
});

const createFlightManagementSlice = (set, get) => ({
  fetchState: "initial",
  flightSessions: null,

  fetchFlightSessions: async () => {
    const { api } = Whitebox;

    const url = api.getPluginProvidedPath("flight.flight-session-list");
    let data = null;

    try {
      const response = await api.client.get(url);
      data = response.data;
    } catch (e) {
      console.error("Failed to fetch flight sessions", e);
      set({ fetchState: "error" });
      return false;
    }

    set({
      flightSessions: data,
      fetchState: "loaded",
    });
    return true;
  },

  getFlightSessions: () => {
    const flightSessions = get().flightSessions;

    if (flightSessions === null) {
      return [];
    }
    return flightSessions;
  },
})

const createFlightPlaybackSlice = (set, get) => ({
  playbackFlightSession: null,
  playbackIsPlaying: false,
  playbackTime: 0,

  playbackPlay: () => {
    const { emit } = get();
    set({ playbackIsPlaying: true });
    emit("player.play");
  },
  playbackPause: () => {
    const { emit } = get();
    set({ playbackIsPlaying: false });
    emit("player.pause");
  },
  playbackToggle: () => {
    const { playbackIsPlaying } = get();
    if (playbackIsPlaying) {
      get().playbackPause();
    } else {
      get().playbackPlay();
    }
  },

  setPlaybackTime: (time, unixTime = false) => {
    const {
      playbackFlightSession,
      emit,
    } = get();

    const startedAt = new Date(playbackFlightSession.started_at);
    const endedAt = new Date(playbackFlightSession.ended_at);
    const totalDuration = (endedAt.getTime() - startedAt.getTime()) / 1000;

    let timeToAssign = time;

    if (unixTime) {
      timeToAssign = time - startedAt.getTime() / 1000;
    }

    if (time < 0) {
      timeToAssign = 0;
    } else if (time > totalDuration) {
      timeToAssign = totalDuration;
    }

    set({ playbackTime: timeToAssign });
    emit("player.time", timeToAssign);
  },

  playbackReset: () => {},
})

const createModeSlice = (set, get) => ({
  // On load, we should be in flight mode
  mode: "flight",

  enterFlightMode: () => set({
    mode: "flight",
    playbackFlightSession: null,
  }),
  enterPlaybackMode: (flightSession) => {
    const {
      mode,
      playbackReset,
    } = get();

    if (mode !== "playback") {
      playbackReset();
    }

    set({
      mode: "playback",
      playbackFlightSession: flightSession,
      sessionKeyMoments: flightSession.key_moments,
    });
  },
});

const useMissionControlStore = create((...a) => ({
  ...createFlightSessionControlSlice(...a),
  ...createFlightManagementSlice(...a),
  ...createFlightPlaybackSlice(...a),
  ...createModeSlice(...a),
  ...createEventHandlingSlice(...a),
}));

export default useMissionControlStore;
