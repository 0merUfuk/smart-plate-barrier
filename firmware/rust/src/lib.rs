#![no_std]
//! Pure state logic candidate. This crate contains no camera, network or GPIO driver.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum State { Closed, OpenWaitingClear }
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Event { NewGrant, AreaClear, Denied, Error }
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Action { None, Open, Close }

pub fn transition(state: State, event: Event) -> (State, Action) {
    match (state, event) {
        (State::Closed, Event::NewGrant) => (State::OpenWaitingClear, Action::Open),
        (State::OpenWaitingClear, Event::AreaClear) => (State::Closed, Action::Close),
        _ => (state, Action::None),
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test] fn open_and_clear() {
        assert_eq!(transition(State::Closed, Event::NewGrant), (State::OpenWaitingClear, Action::Open));
        assert_eq!(transition(State::OpenWaitingClear, Event::AreaClear), (State::Closed, Action::Close));
    }
    #[test] fn errors_do_not_close() {
        assert_eq!(transition(State::OpenWaitingClear, Event::Error), (State::OpenWaitingClear, Action::None));
    }
    #[test] fn repeated_grant_has_no_movement() {
        assert_eq!(transition(State::OpenWaitingClear, Event::NewGrant), (State::OpenWaitingClear, Action::None));
    }
}
