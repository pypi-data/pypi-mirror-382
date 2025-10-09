/**
 * @file
 * @brief Log sink for ZMQ communication
 *
 * @copyright Copyright (c) 2023 DESY and the Constellation authors.
 * This software is distributed under the terms of the EUPL-1.2 License, copied verbatim in the file "LICENSE.md".
 * SPDX-License-Identifier: EUPL-1.2
 */

#pragma once

#include <cstddef>
#include <map>
#include <memory>
#include <mutex>
#include <stop_token>
#include <string>
#include <string_view>
#include <thread>

#include <spdlog/async_logger.h>
#include <spdlog/sinks/base_sink.h>
#include <zmq.hpp>

#include "constellation/core/config/Dictionary.hpp"
#include "constellation/core/log/Level.hpp"
#include "constellation/core/log/Logger.hpp"
#include "constellation/core/metrics/Metric.hpp"
#include "constellation/core/networking/Port.hpp"
#include "constellation/core/utils/string_hash_map.hpp"

namespace constellation::log {
    /**
     * Sink log messages via CMDP
     *
     * Note that ZeroMQ sockets are not thread-safe, meaning that the sink requires a mutex.
     */
    class CMDPSink final : public spdlog::sinks::base_sink<std::mutex> {
    public:
        /**
         * @brief Construct a new CMDPSink
         */
        CMDPSink();

        /**
         * @brief Deconstruct the CMDPSink
         */
        ~CMDPSink() = default;

        // No copy/move constructor/assignment
        /// @cond doxygen_suppress
        CMDPSink(const CMDPSink& other) = delete;
        CMDPSink& operator=(const CMDPSink& other) = delete;
        CMDPSink(CMDPSink&& other) = delete;
        CMDPSink& operator=(CMDPSink&& other) = delete;
        /// @endcond

        /**
         * @brief Get ephemeral port this logger sink is bound to
         *
         * @return Port number
         */
        constexpr networking::Port getPort() const { return port_; }

        /**
         * @brief Set sender name and enable sending by starting the subscription thread
         *
         * @param sender_name Canonical name of the sender
         */
        void enableSending(std::string sender_name);

        /**
         * @brief Disable sending by stopping the subscription thread
         */
        void disableSending();

        /**
         * Sink metric
         *
         * @param metric_value Metric value to sink
         */
        void sinkMetric(metrics::MetricValue metric_value);

        /**
         * Sink notification
         *
         * @param id Notification type
         * @param topics Topics for the given notification type
         */
        void sinkNotification(std::string id, config::Dictionary topics);

    protected:
        void sink_it_(const spdlog::details::log_msg& msg) final;
        void flush_() final {}

    private:
        void subscription_loop(const std::stop_token& stop_token);

        void handle_log_subscriptions(bool subscribe, std::string_view body);

        void handle_stat_subscriptions(bool subscribe, std::string_view body);

    private:
        std::unique_ptr<Logger> logger_;

        // CMDPSink is a shared instance and is destroyed late -> requires shared ownership of the global context
        // otherwise the context will be destroyed before the socket is closed and wait for all sockets to be closed
        std::shared_ptr<zmq::context_t> global_context_;

        zmq::socket_t pub_socket_;
        networking::Port port_;
        std::string sender_name_;

        std::jthread subscription_thread_;
        utils::string_hash_map<std::map<Level, std::size_t>> log_subscriptions_;
        utils::string_hash_map<std::size_t> stat_subscriptions_;
    };

} // namespace constellation::log
