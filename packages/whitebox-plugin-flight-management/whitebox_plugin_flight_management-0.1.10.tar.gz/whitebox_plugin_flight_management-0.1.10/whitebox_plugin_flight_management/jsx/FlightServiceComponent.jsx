import { useEffect } from "react";
import useMissionControlStore from "./stores/mission_control";

const FlightServiceComponent = () => {
  // Immediately on page load, for the entire duration of the app's lifecycle,
  // keep a connection to the `flight` websocket endpoint and keep the mission
  // control state store up to date

  const setActiveFlightSession = useMissionControlStore(
    (store) => store.setActiveFlightSession
  );
  const setActiveKeyMoment = useMissionControlStore(
    (store) => store.setActiveKeyMoment
  );
  const setSessionKeyMoments = useMissionControlStore(
    (store) => store.setSessionKeyMoments
  );

  useEffect(() => {
    return Whitebox.sockets.addEventListener("flight", "message", (event) => {
      const data = JSON.parse(event.data);

      const eligibleTypesForFlightSession = [
        "flight.start",
        "flight.end",
        "on_connect", // This is used to set the initial state on load
      ];
      if (eligibleTypesForFlightSession.includes(data.type)) {
        const { flight_session } = data;
        setActiveFlightSession(flight_session);
      }

      const eligibleTypesForKeyMoments = [
        "flight.key_moment.record",
        "flight.key_moment.finish",
      ]
      if (eligibleTypesForKeyMoments.includes(data.type)) {
        const { key_moment } = data;
        setActiveKeyMoment(key_moment);
      }

      if (data.type === "flight.key_moment.list") {
        const { key_moments, flight_session_id } = data;

        // Fetch data from the store in-place without subscribing.
        // The service component should never re-render!
        const {
          activeFlightSession,
          playbackFlightSession,
        } = useMissionControlStore.getState();

        // If the provided flight session is relevant to the current context
        // (we're flying it, or playing it back), update the relevant state
        if (
            activeFlightSession?.id === flight_session_id
            || playbackFlightSession?.id === flight_session_id
        ) {
          setSessionKeyMoments(key_moments);
        }
      }
    });
  }, []);

  return null;
}

export { FlightServiceComponent };
export default FlightServiceComponent;
