/**
 * @file
 * @brief Command Dialog
 *
 * @copyright Copyright (c) 2024 DESY and the Constellation authors.
 * This software is distributed under the terms of the EUPL-1.2 License, copied verbatim in the file "LICENSE.md".
 * SPDX-License-Identifier: EUPL-1.2
 */

#pragma once

#include <memory>
#include <string>

#include <QDialog>
#include <QMap>
#include <QStandardItemModel>
#include <QStyledItemDelegate>
#include <QStyleOptionViewItem>

#include "constellation/build.hpp"
#include "constellation/core/config/Dictionary.hpp"

// Expose Qt class auto-generated from the user interface XML:
namespace Ui { // NOLINT(readability-identifier-naming)
    class QConnectionDialog;
} // namespace Ui

namespace constellation::gui {

    class ConnectionDialogItemDelegate : public QStyledItemDelegate {
    protected:
        void paint(QPainter* painter, const QStyleOptionViewItem& option, const QModelIndex& index) const override;
    };

    /**
     * @class QConnectionDialog
     * @brief Dialog window to show satellite connection details
     */
    class CNSTLN_API QConnectionDialog : public QDialog {
        Q_OBJECT

    public:
        /**
         * @brief Constructor of the QConnectionDialog
         *
         * @param parent Parent widget of the dialog
         * @param name Name of the satellite
         * @param details Map with connection details
         * @param commands Dictionary with commands of the satellite
         */
        explicit QConnectionDialog(QWidget* parent,
                                   const std::string& name,
                                   const QMap<QString, QVariant>& details,
                                   const config::Dictionary& commands);

    private:
        /** Helper to fill the UI with command dictionary */
        void show_commands(const config::Dictionary& dict);

    private:
        std::shared_ptr<Ui::QConnectionDialog> ui_;
        ConnectionDialogItemDelegate item_delegate_;
    };

} // namespace constellation::gui
