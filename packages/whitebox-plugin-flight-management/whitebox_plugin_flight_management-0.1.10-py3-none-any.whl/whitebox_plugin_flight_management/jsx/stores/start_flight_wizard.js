import { create } from "zustand";

const startFlightWizard = (set, get) => ({
  isOpen: false,
  stepNumber: 1,
  maxStepNumber: 3,
  completeLater: false,

  open: () => set({ isOpen: true }),
  close: () => set({ isOpen: false }),
  nextStep: () =>
    set((state) => {
      if (state.stepNumber < state.maxStepNumber) {
        return { stepNumber: state.stepNumber + 1 };
      }
      return state;
    }),
  setStep: (stepNumber) =>
    set((state) => {
      if (stepNumber >= 1 && stepNumber <= state.maxStepNumber) {
        return { stepNumber };
      }
      return state;
    }),
  setCompleteLater: (completeLater) => set({ completeLater }),
});

const useStartFlightWizardStore = create(startFlightWizard);

export default useStartFlightWizardStore;
